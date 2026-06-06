"""Gera os graficos do PETR4 e salva como PNG."""
import matplotlib
matplotlib.use("Agg")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import yfinance as yf
import warnings
warnings.filterwarnings("ignore")

BG="#08071a"; CARD="#100f2e"; BORDER="#2a2560"
PINK="#f472b6"; CYAN="#38bdf8"; BLUE="#6366f1"
PURPLE="#a78bfa"; LAV="#818cf8"; TEXT="#ede9ff"; MUTED="#8b7ec8"
GREEN="#34d399"; YELLOW="#fbbf24"

plt.rcParams.update({
    "figure.facecolor": BG,"axes.facecolor": CARD,"axes.edgecolor": BORDER,
    "axes.labelcolor": MUTED,"axes.titlecolor": TEXT,"axes.titlesize": 13,
    "axes.labelsize": 10,"axes.titlepad": 14,"axes.spines.top": False,
    "axes.spines.right": False,"axes.grid": True,"grid.color": BORDER,
    "grid.linewidth": 0.6,"xtick.color": MUTED,"ytick.color": MUTED,
    "text.color": TEXT,"font.family": "DejaVu Sans",
    "legend.facecolor": CARD,"legend.edgecolor": BORDER,"legend.labelcolor": TEXT,
})

print("Baixando dados da PETR4...")
df_raw=yf.download("PETR4.SA",period="2y",progress=False)
df=df_raw.copy(); df.columns=df.columns.get_level_values(0)
df["MM30"]=df["Close"].rolling(30).mean()
df["MM90"]=df["Close"].rolling(90).mean()
df["Retorno"]=df["Close"].pct_change()*100
df["Vol21"]=df["Retorno"].rolling(21).std()

# ── FIG 1: Historico ────────────────────────────────────────
fig,axes=plt.subplots(3,1,figsize=(15,12),gridspec_kw={"height_ratios":[3,1.2,1.2]})
fig.patch.set_facecolor(BG)
fig.suptitle("PETR4 - Analise Historica (2 anos)",fontsize=17,fontweight="bold",color=TEXT,y=1.01)

ax1=axes[0]; ax1.set_facecolor(CARD)
close=df["Close"].squeeze(); mm30=df["MM30"].squeeze(); mm90=df["MM90"].squeeze()
ax1.fill_between(df.index,close,close.min(),alpha=0.08,color=CYAN)
ax1.plot(df.index,close,color=CYAN,linewidth=1.5,label="Fechamento",alpha=0.9)
ax1.plot(df.index,mm30,color=YELLOW,linewidth=1.8,label="MM 30 dias",linestyle="--")
ax1.plot(df.index,mm90,color=PINK,linewidth=1.8,label="MM 90 dias",linestyle="-.")
ax1.set_ylabel("Preco (R$)",color=MUTED); ax1.set_title("Preco de Fechamento e Medias Moveis",color=TEXT)
ax1.legend(fontsize=10); ax1.spines["left"].set_color(BORDER); ax1.spines["bottom"].set_color(BORDER)
ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter("R$ %.0f"))
ax1.tick_params(axis="x",labelbottom=False)

ax2=axes[1]; ax2.set_facecolor(CARD)
volume=df["Volume"].squeeze()
colors_vol=[GREEN if r>=0 else PINK for r in df["Retorno"].fillna(0)]
ax2.bar(df.index,volume/1e6,color=colors_vol,alpha=0.7,width=1)
ax2.set_ylabel("Volume (M)",color=MUTED); ax2.set_title("Volume de Negociacoes",color=TEXT)
ax2.spines["left"].set_color(BORDER); ax2.spines["bottom"].set_color(BORDER)
ax2.tick_params(axis="x",labelbottom=False)

ax3=axes[2]; ax3.set_facecolor(CARD)
vol21=df["Vol21"].squeeze()
ax3.fill_between(df.index,vol21,alpha=0.2,color=PURPLE)
ax3.plot(df.index,vol21,color=PURPLE,linewidth=1.5)
ax3.axhline(vol21.mean(),color=YELLOW,linewidth=1.3,linestyle="--",alpha=0.8,label=f"Media: {vol21.mean():.2f}%")
ax3.set_ylabel("Volatilidade (%)",color=MUTED); ax3.set_title("Volatilidade Rolante 21 dias",color=TEXT)
ax3.legend(fontsize=9); ax3.spines["left"].set_color(BORDER); ax3.spines["bottom"].set_color(BORDER)
ax3.xaxis.set_major_formatter(mdates.DateFormatter("%b/%y"))
ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

plt.tight_layout()
plt.savefig("petr4_historico.png",dpi=150,bbox_inches="tight",facecolor=BG); plt.close()
print("Salvo: petr4_historico.png")

# ── FIG 2: Retornos ─────────────────────────────────────────
fig,axes=plt.subplots(1,2,figsize=(14,5)); fig.patch.set_facecolor(BG)
fig.suptitle("PETR4 - Distribuicao de Retornos",fontsize=15,fontweight="bold",color=TEXT)

ret=df["Retorno"].dropna().squeeze()
ax=axes[0]; ax.set_facecolor(CARD)
positivos=ret[ret>=0]; negativos=ret[ret<0]
ax.hist(negativos,bins=40,color=PINK,alpha=0.8,label="Negativo",edgecolor="none")
ax.hist(positivos,bins=40,color=GREEN,alpha=0.8,label="Positivo",edgecolor="none")
ax.axvline(ret.mean(),color=YELLOW,linewidth=2,linestyle="--",label=f"Media: {ret.mean():.2f}%")
ax.axvline(0,color=MUTED,linewidth=1,alpha=0.5)
ax.set_xlabel("Retorno Diario (%)",color=MUTED); ax.set_ylabel("Frequencia",color=MUTED)
ax.set_title("Distribuicao de Retornos Diarios",color=TEXT); ax.legend(fontsize=9)
ax.spines["left"].set_color(BORDER); ax.spines["bottom"].set_color(BORDER)
stats_txt=(f"Desvio Padrao: {ret.std():.2f}%\nMaximo: +{ret.max():.2f}%\nMinimo: {ret.min():.2f}%\nSharpe aprox.: {ret.mean()/ret.std():.2f}")
ax.text(0.97,0.95,stats_txt,transform=ax.transAxes,va="top",ha="right",fontsize=9,color=TEXT,
    bbox=dict(facecolor=BORDER,edgecolor="none",alpha=0.7,pad=6))

ax=axes[1]; ax.set_facecolor(CARD)
df_ret=df[["Retorno"]].copy().dropna(); df_ret["Mes"]=df_ret.index.to_period("M")
meses=sorted(df_ret["Mes"].unique())[-12:]
dados_box=[df_ret[df_ret["Mes"]==m]["Retorno"].values for m in meses]
labels_box=[str(m) for m in meses]
bp=ax.boxplot(dados_box,patch_artist=True,
    medianprops=dict(color=YELLOW,linewidth=2),whiskerprops=dict(color=MUTED,linewidth=1.2),
    capprops=dict(color=MUTED,linewidth=1.2),flierprops=dict(marker="o",markerfacecolor=PINK,markersize=3,alpha=0.5))
for box in bp["boxes"]: box.set_facecolor(BLUE+"55"); box.set_edgecolor(LAV)
ax.set_xticklabels(labels_box,rotation=35,ha="right",fontsize=7.5,color=MUTED)
ax.axhline(0,color=MUTED,linewidth=1,alpha=0.5,linestyle="--")
ax.set_ylabel("Retorno Diario (%)",color=MUTED); ax.set_title("Boxplot de Retornos - Ultimos 12 Meses",color=TEXT)
ax.spines["left"].set_color(BORDER); ax.spines["bottom"].set_color(BORDER)

plt.tight_layout()
plt.savefig("petr4_retornos.png",dpi=150,bbox_inches="tight",facecolor=BG); plt.close()
print("Salvo: petr4_retornos.png")
print("Todos os graficos gerados!")
