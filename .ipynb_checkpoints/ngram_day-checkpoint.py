# -*- coding: utf-8 -*-

import streamlit as st
import dhlab_v2 as d2
import pandas as pd
from PIL import Image


@st.cache(suppress_st_warning=True, show_spinner = False)
def sumword(words, period):
    wordlist =   [x.strip() for x in words.split(',')]
    # check if trailing comma, or comma in succession, if so count comma in
    if '' in wordlist:
        wordlist = [','] + [y for y in wordlist if y != '']
    ref = d2.ngram_news(wordlist, period = period).sum(axis = 1)
    ref.columns = 'tot'
    return ref


@st.cache(suppress_st_warning=True, show_spinner = False)
def ngram(word, period, smooth_slider):
    res = pd.DataFrame()
    #if " " in word:
    #   bigram = word.split()[:2]
    #    print('bigram i kjømda')
    #    #res = nb.bigram(first = bigram [0], second = bigram [1], ddk = ddk, topic = subject, period = period)
    #else:

    res = d2.ngram_news(word, period = (period_slider[0], period_slider[1]))
    res.index = res.index.map(pd.Timestamp)
    
#    if sammenlign != "":
#        tot = sumword(sammenlign, period=(period_slider[0], period_slider[1]))
#        for x in res:
#            res[x] = res[x]/tot
    res = res.rolling(window = smooth_slider).mean()

    return res



image = Image.open('NB-logo-no-eng-svart.png')
st.image(image, width = 200)
st.markdown('Se mer om å drive analytisk DH på [DHLAB-siden](https://nbviewer.jupyter.org/github/DH-LAB-NB/DHLAB/blob/master/DHLAB_ved_Nasjonalbiblioteket.ipynb), og korpusanalyse via web [her](https://beta.nb.no/korpus/)')


st.title('Dagsplott for aviser')

st.markdown('### Trendlinjer')

st.sidebar.header('Input')
words = st.text_input('Fyll inn ord eller bigram adskilt med komma. Det skilles mellom store og små bokstaver', "")
if words == "":
    words = "og"

#sammenlign = st.sidebar.text_input("Sammenling med summen av følgende ord - sum av komma og punktum er standard, som gir tilnærmet 10nde-del av inputordenes relativfrekvens", ".,")

allword = list(set([w.strip() for w in words.split(',')]))[:30]



import datetime

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days = 1)
start_date = st.date_input('Startdato', today - datetime.timedelta(days = 400))
end_date = st.date_input('Sluttdato', today)
delta = end_date - start_date
if delta.days < 1000:
    period_slider = (start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))
    #st.write(period_slider)
else:
    st.write('dagsplott ikke over 3 år')
    
    
# wrapper for nb.frame() check if dataframe is empty before assigning names to columns
def frm(x, y):
    if not x.empty:
        res = pd.DataFrame(x, columns = [y])
    else:
        res = x
    return res

st.sidebar.header('Visning')
smooth_slider = st.sidebar.slider('Glatting', 1, 21, 7)

if delta.days < 1000 and delta.days > 0:
    df = ngram(allword, (period_slider[0], period_slider[1]), smooth_slider)
    st.line_chart(df)

