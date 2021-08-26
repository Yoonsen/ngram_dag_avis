# -*- coding: utf-8 -*-

import streamlit as st
import dhlab_v2 as d2
import pandas as pd
from PIL import Image

import datetime

max_days = 730
min_days = 3

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
def ngram(word, mid_date, sammenlign):
    #st.write('innom')
    period = ((mid_date - datetime.timedelta(days = max_days)).strftime("%Y%m%d"),
              (mid_date + datetime.timedelta(days = max_days)).strftime("%Y%m%d"))
    res = d2.ngram_news(word, period = period)
    res.index = res.index.map(pd.Timestamp)
    
    if sammenlign != "":
        tot = sumword(sammenlign, period = period)
        for x in res:
            res[x] = res[x]/tot

    return res

@st.cache(suppress_st_warning = True, show_spinner = False)
def adjust(df, date, days, smooth):
    ts = pd.Timestamp(date)
    td = pd.Timedelta(days = days - 1)
    s = pd.Timestamp(min(pd.Timestamp.today(), pd.Timestamp((ts - pd.Timedelta(days = days + min_days)))).strftime("%Y%m%d"))
    e = pd.Timestamp(min(pd.Timestamp.today(), pd.Timestamp((ts + td))).strftime("%Y%m%d"))
    mask = (df.index >= s) & (df.index <= e)
    #st.write(s,e)
    #st.write(df.loc[s])
    res = df.loc[mask].rolling(window = smooth).mean()
    return res


image = Image.open('NB-logo-no-eng-svart.png')
st.image(image, width = 200)
st.markdown('Se mer om å drive analytisk DH på [DHLAB-siden](https://nbviewer.jupyter.org/github/DH-LAB-NB/DHLAB/blob/master/DHLAB_ved_Nasjonalbiblioteket.ipynb), og korpusanalyse via web [her](https://beta.nb.no/korpus/)')


st.title('Dagsplott for aviser')

st.markdown('### Trendlinjer')

################################### Sammenlign ##################################

st.sidebar.header('Input')
words = st.text_input('Skriv inn ett eller flere enkeltord adskilt med komma. Det er forskjell på store og små bokstaver', "frihet")

sammenlign = st.sidebar.text_input("Sammenlingn med summen av en liste med ord. Om listen ikke er tom viser y-aksen antall forekomster pr summen av ordene det sammenlignes med. Er listen tom viser y-aksen antall forekomster", "")

allword = list(set([w.strip() for w in words.split(',')]))[:30]


#################################### Glatting ############################################

st.sidebar.header('Visning')
smooth_slider = st.sidebar.slider('Glatting', 1, 21, 3)


#########################  Angi periode ##################################

st.sidebar.title("Periode")

st.sidebar.write("Velg lengde på periode og midt-dato")
mid_date = st.sidebar.date_input('Dato', datetime.datetime.today() - datetime.timedelta(days = 183))
period_size = st.sidebar.number_input("Antall dager før og etter, maks 730, minimum 100", min_value= min_days, max_value = max_days, value = 183)



### Beregn start og slutt, og vis frem graf

start_date = min(datetime.date.today() - datetime.timedelta(days = 2), mid_date - datetime.timedelta(days = period_size))
end_date = min(datetime.date.today(), mid_date + datetime.timedelta(days = period_size))

period = (start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))
#st.write(mid_date, period)

## init values

df = ngram(allword, mid_date, sammenlign)
#st.write(df.index)
df_show = adjust(df, mid_date, period_size, smooth_slider)
st.line_chart(df_show)






