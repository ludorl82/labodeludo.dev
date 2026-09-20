function prompt_my_context() {
  local glyphs=( $'®' $'¶' $'¿' $'Æ' $'Þ' $'ß' $'µ' $'©' $'§' $'¥' $'¤' $'£' $'¢' $'æ' $'±' $'¡' $'¦' $'ª' $'¬' )
  local glyph="${glyphs[$(( RANDOM % ${#glyphs[@]} + 1 ))]}"
  p10k segment -b 0 -f 7 -t "ludo ${glyph} %D{%T}"
}
