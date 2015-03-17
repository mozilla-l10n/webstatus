#! /usr/bin/env bash

# No parameters
if [ $# -lt 1 ]
then
    echo "Script requires at least one parameter (.po file to analyze)."
    exit
fi

translated=$(msgattrib $1 --translated --no-obsolete --no-fuzzy | grep -c 'msgid ')
if [ $translated -gt 0 ]
then
    translated=$(($translated-1))
fi

untranslated=$(msgattrib $1 --untranslated --no-obsolete --no-fuzzy | grep -c 'msgid ')
if [ $untranslated -gt 0 ]
then
    untranslated=$(($untranslated-1))
fi

fuzzy=$(msgattrib $1 --only-fuzzy --no-obsolete | grep -c 'msgid ')
if [ $fuzzy -gt 0 ]
then
    fuzzy=$(($fuzzy-1))
fi

total=$(($translated+$untranslated+$fuzzy))

echo "{"
echo "    \"fuzzy\": $fuzzy,"
echo "    \"translated\": $translated,"
echo "    \"total\": $total,"
echo "    \"untranslated\": $untranslated"
echo "}"
