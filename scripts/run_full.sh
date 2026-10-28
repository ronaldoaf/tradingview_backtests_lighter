#!/bin/bash
# Roda todos os lotes com FULL=1 num ativo (series diarias para o tvo.py), J processos em paralelo.
# uso: ATIVO=xag J=4 bash scripts/run_full.sh   -> results/<ATIVO>_4p_8p_full/
cd "$(dirname "$0")/.."; mkdir -p results/${ATIVO}_4p_8p_full logs
L="$(seq 3 38) flawless ichimoku rsidiv vixfix zigzagpa"
printf '%s\n' $L | xargs -P ${J:-4} -I{} sh -c "ATIVO=$ATIVO SUF=_8p NP=8 FULL=1 python scripts/study_us100_4p.py {} > logs/${ATIVO}_full_{}.log 2>&1; tail -1 logs/${ATIVO}_full_{}.log"
