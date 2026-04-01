#!/usr/bin/env bash
# KodeKeeper — Claude Code status line
# Format: KK | ctx bar | free | day/wk/mo | model | dir[branch] | time

input=$(cat)
USAGE_FILE="$HOME/.claude/usage/totals.json"
mkdir -p "$HOME/.claude/usage"

# ── Parse JSON ────────────────────────────────────────────────────────────────

total_tokens=$(echo "$input" | jq -r '.context_window.context_window_size // 0')
input_tokens=$(echo "$input" | jq -r '.context_window.current_usage.input_tokens // 0')
used_pct=$(echo "$input"    | jq -r '.context_window.used_percentage // empty')
total_in=$(echo "$input"    | jq -r '.context_window.total_input_tokens // 0')
total_out=$(echo "$input"   | jq -r '.context_window.total_output_tokens // 0')
session_total=$(( total_in + total_out ))

model_raw=$(echo "$input" | jq -r '.model.display_name // .model // "?"')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
agent_name=$(echo "$input" | jq -r '.agent.name // empty')

# ── Shorten model name ────────────────────────────────────────────────────────

model_short="$model_raw"
case "$model_raw" in
  *"claude-sonnet-4-6"*|*"Sonnet 4.6"*|*"sonnet-4-6"*) model_short="Sonnet 4.6" ;;
  *"claude-opus-4"*|*"Opus 4"*)                         model_short="Opus 4"     ;;
  *"claude-haiku-4"*|*"Haiku 4"*)                       model_short="Haiku 4.5"  ;;
  *"claude-3-5-sonnet"*|*"Sonnet 3.5"*)                 model_short="Sonnet 3.5" ;;
  *"claude-3-opus"*|*"Opus 3"*)                         model_short="Opus 3"     ;;
  *"claude-3-haiku"*|*"Haiku 3"*)                       model_short="Haiku 3"    ;;
  Unknown*|"?") model_short="no session" ;;
esac

# ── Dir + git branch ──────────────────────────────────────────────────────────

dir=$(basename "$cwd")
branch=""
if [ -n "$cwd" ] && [ -d "$cwd/.git" ] || git -C "$cwd" rev-parse --git-dir &>/dev/null 2>&1; then
  branch=$(git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null)
fi
if [ -n "$branch" ]; then
  dir_str="${dir}[${branch}]"
else
  dir_str="${dir}"
fi

# ── Format token counts ───────────────────────────────────────────────────────

fmt() {
  local n="$1"
  n="${n:-0}"
  if [ "$n" -ge 1000000 ] 2>/dev/null; then
    printf "%.1fM" "$(echo "scale=1; $n / 1000000" | bc 2>/dev/null || echo 0)"
  elif [ "$n" -ge 1000 ] 2>/dev/null; then
    echo "$(( n / 1000 ))k"
  else
    echo "${n}"
  fi
}

free_tokens=$(( total_tokens - input_tokens ))
free_k=$(fmt "$free_tokens")

# ── Context bar (10-char) ─────────────────────────────────────────────────────

ctx_bar="----------"
ctx_label="--"
if [ -n "$used_pct" ]; then
  pct_int=$(printf "%.0f" "$used_pct")
  filled=$(( pct_int / 10 ))
  [ "$filled" -gt 10 ] && filled=10
  empty=$(( 10 - filled ))
  bar=""
  for ((i=0; i<filled; i++)); do bar="${bar}█"; done
  for ((i=0; i<empty;  i++)); do bar="${bar}░"; done
  ctx_bar="$bar"
  ctx_label="${pct_int}%"
fi

# ── Context health tag ────────────────────────────────────────────────────────

health="OK"
if [ -n "$used_pct" ]; then
  pct_int=$(printf "%.0f" "$used_pct")
  if   [ "$pct_int" -ge 85 ]; then health="!! RESET NOW"
  elif [ "$pct_int" -ge 70 ]; then health="!! FILLING"
  elif [ "$pct_int" -ge 50 ]; then health=">"
  else                              health="OK"
  fi
fi

# ── Usage tracking (day / week / month) ──────────────────────────────────────

today=$(date +%Y-%m-%d)
this_week=$(date +%Y-W%V)
this_month=$(date +%Y-%m)

# Load existing totals
if [ -f "$USAGE_FILE" ]; then
  saved_day=$(jq -r '.day.date // ""'        "$USAGE_FILE" 2>/dev/null)
  saved_day_tok=$(jq -r '.day.tokens // 0'   "$USAGE_FILE" 2>/dev/null)
  saved_wk=$(jq -r '.week.week // ""'        "$USAGE_FILE" 2>/dev/null)
  saved_wk_tok=$(jq -r '.week.tokens // 0'   "$USAGE_FILE" 2>/dev/null)
  saved_mo=$(jq -r '.month.month // ""'      "$USAGE_FILE" 2>/dev/null)
  saved_mo_tok=$(jq -r '.month.tokens // 0'  "$USAGE_FILE" 2>/dev/null)
  saved_sess=$(jq -r '.last_session_total // 0' "$USAGE_FILE" 2>/dev/null)
else
  saved_day="" saved_day_tok=0
  saved_wk=""  saved_wk_tok=0
  saved_mo=""  saved_mo_tok=0
  saved_sess=0
fi

# Compute delta since last statusline update
delta=$(( session_total - saved_sess ))
[ "$delta" -lt 0 ] && delta=0   # new session → no rollover

# Reset counters on period boundaries
[ "$saved_day" != "$today" ]      && saved_day_tok=0
[ "$saved_wk"  != "$this_week" ]  && saved_wk_tok=0
[ "$saved_mo"  != "$this_month" ] && saved_mo_tok=0

# Accumulate
day_tok=$(( saved_day_tok + delta ))
wk_tok=$(( saved_wk_tok + delta ))
mo_tok=$(( saved_mo_tok + delta ))

# Context history (for oscilloscope — append latest pct, keep last 120)
ctx_pct_val="0"
[ -n "$used_pct" ] && ctx_pct_val=$(printf "%.1f" "$used_pct")

existing_hist="[]"
if [ -f "$USAGE_FILE" ]; then
  existing_hist=$(jq -r '.ctx_history // []' "$USAGE_FILE" 2>/dev/null || echo "[]")
fi
new_hist=$(echo "$existing_hist" | jq --argjson p "$ctx_pct_val" '. + [$p] | .[-120:]' 2>/dev/null || echo "[$ctx_pct_val]")

# Session start tracking
existing_sess_start=""
if [ -f "$USAGE_FILE" ]; then
  existing_sess_start=$(jq -r '.session_start // ""' "$USAGE_FILE" 2>/dev/null)
fi
# Reset session start if session_total dropped (new session)
if [ "$delta" -le 0 ] && [ "$session_total" -lt 5000 ]; then
  existing_sess_start=$(date -Iseconds)
fi
[ -z "$existing_sess_start" ] && existing_sess_start=$(date -Iseconds)

# Free tokens in K for dashboard
free_k_raw=$(fmt "$free_tokens")

# Persist (best-effort, silent on failure)
jq -n \
  --arg day "$today" --argjson dtok "$day_tok" \
  --arg wk  "$this_week" --argjson wtok "$wk_tok" \
  --arg mo  "$this_month" --argjson mtok "$mo_tok" \
  --argjson sess "$session_total" \
  --argjson hist "$new_hist" \
  --arg model "$model_short" \
  --arg sess_start "$existing_sess_start" \
  --arg free_k "$free_k_raw" \
  '{
    last_session_total: $sess,
    model:        $model,
    ctx_history:  $hist,
    ctx_free_k:   $free_k,
    session_start: $sess_start,
    day:   {date:  $day, tokens: $dtok},
    week:  {week:  $wk,  tokens: $wtok},
    month: {month: $mo,  tokens: $mtok}
  }' > "$USAGE_FILE" 2>/dev/null

day_fmt=$(fmt "$day_tok")
wk_fmt=$(fmt "$wk_tok")
mo_fmt=$(fmt "$mo_tok")

# ── Time ──────────────────────────────────────────────────────────────────────

now=$(date +%H:%M)

# ── Agent suffix ──────────────────────────────────────────────────────────────

agent_str=""
[ -n "$agent_name" ] && agent_str=" ~${agent_name}"

# ── Assemble ──────────────────────────────────────────────────────────────────

printf "Kode Keeper [%s] %s %s  |  %s free  |  d:%s w:%s m:%s  |  %s  |  %s%s  |  %s\n" \
  "$health" \
  "$ctx_bar" \
  "$ctx_label" \
  "$free_k" \
  "$day_fmt" "$wk_fmt" "$mo_fmt" \
  "$model_short" \
  "$dir_str" \
  "$agent_str" \
  "$now"
