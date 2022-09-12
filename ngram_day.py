# -*- coding: utf-8 -*-

import streamlit as st
import dhlab.api.dhlab_api as api
import pandas as pd
from PIL import Image
import json
import datetime
import matplotlib.pyplot as plt

max_days = 3700
min_days = 3

@st.cache(suppress_st_warning=True, show_spinner = False)
def titles():
    return json.load(open('titles.json', encoding = 'utf-8'))

@st.cache(suppress_st_warning=True, show_spinner = False)
def sumword(words, period, title = None):
    wordlist =   [x.strip() for x in words.split(',')]
    # check if trailing comma, or comma in succession, if so count comma in
    if '' in wordlist:
        wordlist = [','] + [y for y in wordlist if y != '']
    try:
        ref = api.ngram_news(wordlist, period = period, title = title).sum(axis = 1)
        ref.columns = 'tot'
        ref.index = ref.index.map(pd.Timestamp)
    except AttributeError:
        st.write('...tom ramme for sammenligning ...')
        ref = pd.DataFrame()
    return ref


@st.cache(suppress_st_warning=True, show_spinner = False)
def ngram(word, mid_date, sammenlign, title = None):
    #st.write('innom')
    period = ((mid_date - datetime.timedelta(days = max_days)).strftime("%Y%m%d"),
              (mid_date + datetime.timedelta(days = max_days)).strftime("%Y%m%d"))
    try:
        res = api.ngram_news(word, period = period, title = title).fillna(0).sort_index()
        res.index = res.index.map(pd.Timestamp)

        if sammenlign != "":
            tot = sumword(sammenlign, period = period, title = title)
            for x in res:
                res[x] = res[x]/tot
    except AttributeError:
        st.write('... tom ramme for ord ...')
        res = pd.DataFrame()
    return res

@st.cache(suppress_st_warning = True, show_spinner = False)
def adjust(df, date, days, smooth):
    res = df
    
    try:
        ts = pd.Timestamp(date)
        td = pd.Timedelta(days = days - 1)
        s = pd.Timestamp(min(pd.Timestamp("20210701"), pd.Timestamp((ts - pd.Timedelta(days = days + min_days)))).strftime("%Y%m%d"))
        e = pd.Timestamp(min(pd.Timestamp.today(), pd.Timestamp((ts + td))).strftime("%Y%m%d"))
        mask = (df.index >= s) & (df.index <= e)
        
        #st.write(s,e)
        #st.write(df.loc[s])
        
        res = df.loc[mask].rolling(window = smooth).mean()
    
    except AttributeError:
        st.write('...tom ramme...')
    
    return res


image = Image.open('DHlab_logo_web_en_black.png')
st.sidebar.image(image, width = 200)
st.sidebar.markdown('Les mer på [DHLAB-siden](https://nb.no/dh-lab/)')


st.title('Dagsplott for aviser')

st.markdown('### Trendlinjer')

################################### Sammenlign ##################################


words = st.text_input('Skriv inn ett eller flere enkeltord adskilt med komma. Det er forskjell på store og små bokstaver', "frihet")

st.sidebar.header('Input')
sammenlign = st.sidebar.text_input("Sammenlingn med summen av en liste med ord. Om listen ikke er tom viser y-aksen antall forekomster pr summen av ordene det sammenlignes med. Er listen tom viser y-aksen antall forekomster", "")

allword = list(set([w.strip() for w in words.split(',')]))[:30]

avisnavn = st.sidebar.selectbox("Begynn å skrive navnet på en avis, og velg fra listen", titles(), index=0)
if avisnavn == "--ingen--":
    avisnavn = None

#st.write(avisnavn)
#################################### Glatting ############################################

st.sidebar.header('Visning')

smooth_slider = st.sidebar.slider('Glatting', 1, 21, 3)

graftype = st.sidebar.selectbox('Matplotlib eller Streamlit', ['Matplotlib', 'Streamlit'], index = 1)
if graftype == 'Matplotlib':
    alfa = st.sidebar.number_input('Gjennomsiktighet', min_value = 0.1, max_value = 1., value = 0.9)
    width = st.sidebar.number_input('Linjetykkelse', min_value = 0.1, max_value = 5., value = 0.8)
    
last_date = datetime.datetime.strptime("20200701", '%Y%m%d')

#########################  Angi periode ##################################

st.sidebar.title("Periode")

st.sidebar.markdown("Velg dato og lengde på periode, antall dager før og etter")


mid_date = st.sidebar.date_input('Dato', last_date - datetime.timedelta(days = int(max_days/2)))

period_size = st.sidebar.number_input(f"Lengde på periode i antall dager, maks {max_days}, minimum {min_days}", min_value= min_days, max_value = max_days, value = max_days)
 

### Beregn start og slutt, og vis frem graf

start_date = min(datetime.date.today() - datetime.timedelta(days = 2), mid_date - datetime.timedelta(days = period_size))
end_date = min(datetime.date.today(), mid_date + datetime.timedelta(days = period_size))

period = (start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))

def show_data(data, alfa = 0.9, width = 0.8):
    fontsize = 12

    fig, ax = plt.subplots() #nrows=2, ncols=2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.spines["bottom"].set_color("grey")
    ax.spines["left"].set_color("grey")
    ax.spines["bottom"].set_linewidth(0.5)
    ax.spines["left"].set_linewidth(0.5)
    ax.legend(loc='upper left', frameon=False)
    ax.spines["left"].set_visible(True)

    plt.rcParams.update({'font.size': 8,
                        'font.family': 'monospace',
                        'font.monospace':'Courier'})

    plt.legend(loc = 2, prop = {
        'size': fontsize})
    #plt.xlabel('Ordliste', fontsize= fontsize*0.8)
    #plt.ylabel('Frekvensvekt', fontsize= fontsize*0.8)
    data.plot(ax=ax, figsize = (8,4), kind='line', rot=20, alpha = alfa, lw = width)

    st.pyplot(fig)

    #st.write('som tabell')
    #st.write(data.style.background_gradient())
         
## init values

df = ngram(allword, mid_date, sammenlign, title = avisnavn)
#st.write(df.index)

#### ------------- Plot the graf -----------------

df_show = adjust(df, mid_date, period_size, smooth_slider)
if graftype == 'Matplotlib':
    show_data(df_show, alfa, width)
elif graftype == 'Streamlit':
    st.line_chart(df_show)
else:
    st.line_chart(df_show)




