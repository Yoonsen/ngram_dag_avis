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
    ref.index = ref.index.map(pd.Timestamp)
    return ref


@st.cache(suppress_st_warning=True, show_spinner = False)
def ngram(word, period, smooth_slider, sammenlign):
    
    res = d2.ngram_news(word, period = (period_slider[0], period_slider[1]))
    res.index = res.index.map(pd.Timestamp)
    
    if sammenlign != "":
        tot = sumword(sammenlign, period=(period_slider[0], period_slider[1]))
        for x in res:
            res[x] = res[x]/tot
    
    res = res.rolling(window = smooth_slider).mean()

    return res



image = Image.open('NB-logo-no-eng-svart.png')
st.image(image, width = 200)
st.markdown('Se mer om å drive analytisk DH på [DHLAB-siden](https://nbviewer.jupyter.org/github/DH-LAB-NB/DHLAB/blob/master/DHLAB_ved_Nasjonalbiblioteket.ipynb), og korpusanalyse via web [her](https://beta.nb.no/korpus/)')


st.title('Dagsplott for aviser')

st.markdown('### Trendlinjer')

################################### Sammenlign ##################################

st.sidebar.header('Input')
words = st.text_input('Fyll inn ord eller bigram adskilt med komma. Det skilles mellom store og små bokstaver', "frihet")

sammenlign = st.sidebar.text_input("Sammenlingn med summen av en liste med ord. Om listen ikke er tom viser y-aksen antall forekomster pr summen av ordene det sammenlignes med. Er listen tom viser y-aksen antall forekomster", "")


#################################### Glatting ############################################

st.sidebar.header('Visning')
smooth_slider = st.sidebar.slider('Glatting', 1, 21, 7)



allword = list(set([w.strip() for w in words.split(',')]))[:30]



import datetime

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days = 1)

#########################  Angi periode ##################################
st.sidebar.title("Periode")
st.sidebar.write("Velg periode. Angi siste dato av en periode på 3 år")


end_date = st.sidebar.date_input('', today)
start_date = end_date - datetime.timedelta(days = 1100)

delta = end_date - start_date
period_slider = (start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))

df = ngram(allword, (period_slider[0], period_slider[1]), smooth_slider, sammenlign)
st.line_chart(df)






