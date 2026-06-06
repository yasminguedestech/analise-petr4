"""Gera os graficos do PETR4 — design moderno, fundo branco."""
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

# ── Paleta moderna — branco + amarelos claros ────────────────
BG       = "#FFFFFF"
BORDER   = "#F0EFE9"
TEXT     = "#1C1917"
MUTED    = "#78716C"

Y_BRIGHT = "#FACC15"   # amarelo vivo  → linha principal / destaque
Y_MID    = "#EAB308"   # dourado       → MM30 / referência
Y_LIGHT  = "#FEF08A"   # amarelo claro → fill de área
Y_DEEP   = "#CA8A04"   # âmbar escuro  → MM90 / negativo
Y_WARM   = "#F59E0B"   # âmbar médio   → volatilidade

plt.rcParams.update({
    "figure.facecolor":   BG,
    "axes.facecolor":     BG,
    "axes.edgecolor":     BORDER,
    "axes.labelcolor":    MUTED,
    "axes.titlecolor":    TEXT,
    "axes.titlesize":     12,
    "axes.labelsize":     9,
    "axes.titlepad":      12,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.spines.left":   False,
    "axes.spines.bottom": True,
    "axes.grid":          True,
    "grid.color":         "#F5F5F0",
    "grid.linewidth":     0.7,
    "xtick.color":        MUTED,
    "ytick.color":        MUTED,
    "text.color":         TEXT,
    "font.family":        "DejaVu Sans",
    "legend.facecolor":   BG,
    "legend.edgecolor":   BORDER,
    "legend.labelcolor":  TEXT,
    "legend.framealpha":  1,
})

print("Baixando dados da PETR4...")
df_raw = yf.download("PETR4.SA", period="2y", progress=False)
df = df_raw.copy(); df.columns = df.columns.get_level_values(0)
df["MM30"]    = df["Close"].rolling(30).mean()
df["MM90"]    = df["Close"].rolling(90).mean()
df["Retorno"] = df["Close"].pct_change() * 100
df["Vol21"]   = df["Retorno"].rolling(21).std()

# ── FIG 1: Histórico ────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(15, 12),
                         gridspec_kw={"height_ratios": [3, 1.2, 1.2]})
fig.patch.set_facecolor(BG)
fig.suptitle("PETR4 — Análise Histórica (2 anos)",
             fontsize=17, fontweight="bold", color=TEXT, y=1.01)

# Painel 1: Preço + MMs
ax1 = axes[0]; ax1.set_facecolor(BG)
close = df["Close"].squeeze()
mm30  = df["MM30"].squeeze()
mm90  = df["MM90"].squeeze()
ax1.fill_between(df.index, close, close.min(), alpha=0.12, color=Y_LIGHT)
ax1.plot(df.index, close, color=Y_BRIGHT, linewidth=1.6, label="Fechamento", alpha=0.95)
ax1.plot(df.index, mm30,  color=Y_MID,    linewidth=1.8, label="MM 30 dias", linestyle="--")
ax1.plot(df.index, mm90,  color=Y_DEEP,   linewidth=1.8, label="MM 90 dias", linestyle="-.")
ax1.set_ylabel("Preço (R$)")
ax1.set_title("Preço de Fechamento e Médias Móveis")
ax1.legend(fontsize=10, frameon=False)
ax1.spines["bottom"].set_color(BORDER)
ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter("R$ %.0f"))
ax1.tick_params(axis="x", labelbottom=False)

# Painel 2: Volume
ax2 = axes[1]; ax2.set_facecolor(BG)
volume = df["Volume"].squeeze()
colors_vol = [Y_BRIGHT if r >= 0 else Y_DEEP for r in df["Retorno"].fillna(0)]
ax2.bar(df.index, volume / 1e6, color=colors_vol, alpha=0.75, width=1, linewidth=0)
ax2.set_ylabel("Volume (M)")
ax2.set_title("Volume de Negociações")
ax2.spines["bottom"].set_color(BORDER)
ax2.tick_params(axis="x", labelbottom=False)

# Painel 3: Volatilidade rolante
ax3 = axes[2]; ax3.set_facecolor(BG)
vol21 = df["Vol21"].squeeze()
ax3.fill_between(df.index, vol21, alpha=0.18, color=Y_WARM)
ax3.plot(df.index, vol21, color=Y_MID, linewidth=1.6)
ax3.axhline(vol21.mean(), color=Y_DEEP, linewidth=1.4, linestyle="--",
            alpha=0.9, label=f"Média  {vol21.mean():.2f}%")
ax3.set_ylabel("Volatilidade (%)")
ax3.set_title("Volatilidade Rolante 21 dias")
ax3.legend(fontsize=9, frameon=False)
ax3.spines["bottom"].set_color(BORDER)
ax3.xaxis.set_major_formatter(mdates.DateFormatter("%b/%y"))
ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

plt.tight_layout(pad=2.5)
plt.savefig("petr4_historico.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Salvo: petr4_historico.png")

# ── FIG 2: Retornos ─────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
fig.patch.set_facecolor(BG)
fig.suptitle("PETR4 — Distribuição de Retornos",
             fontsize=15, fontweight="bold", color=TEXT)

ret = df["Retorno"].dropna().squeeze()

# Histograma
ax = axes[0]; ax.set_facecolor(BG)
ax.hist(ret[ret < 0],  bins=40, color=Y_DEEP,   alpha=0.80, label="Negativo", edgecolor=BG, linewidth=0.5)
ax.hist(ret[ret >= 0], bins=40, color=Y_BRIGHT,  alpha=0.80, label="Positivo", edgecolor=BG, linewidth=0.5)
ax.axvline(ret.mean(), color=Y_MID, linewidth=2, linestyle="--",
           label=f"Média  {ret.mean():.2f}%")
ax.axvline(0, color=MUTED, linewidth=1, alpha=0.4)
ax.set_xlabel("Retorno Diário (%)"); ax.set_ylabel("Frequência")
ax.set_title("Distribuição de Retornos Diários")
ax.legend(fontsize=9, frameon=False)
ax.spines["bottom"].set_color(BORDER)
stats_txt = (
    f"Desvio Padrão:  {ret.std():.2f}%\n"
    f"Máximo:  +{ret.max():.2f}%\n"
    f"Mínimo:  {ret.min():.2f}%\n"
    f"Sharpe aprox.:  {ret.mean()/ret.std():.2f}"
)
ax.text(0.97, 0.96, stats_txt, transform=ax.transAxes, va="top", ha="right",
        fontsize=9, color=MUTED,
        bbox=dict(facecolor=BORDER, edgecolor="none", alpha=0.9, pad=7))

# Boxplot mensal
ax = axes[1]; ax.set_facecolor(BG)
df_ret = df[["Retorno"]].copy().dropna()
df_ret["Mes"] = df_ret.index.to_period("M")
meses = sorted(df_ret["Mes"].unique())[-12:]
dados_box  = [df_ret[df_ret["Mes"]==m]["Retorno"].values for m in meses]
labels_box = [str(m) for m in meses]
bp = ax.boxplot(dados_box, patch_artist=True,
                medianprops=dict(color=TEXT, linewidth=2),
                whiskerprops=dict(color=MUTED, linewidth=1.2),
                capprops=dict(color=MUTED, linewidth=1.2),
                flierprops=dict(marker="o", markerfacecolor=BORDER,
                                markeredgecolor=MUTED, markersize=3, alpha=0.6))
for box in bp["boxes"]:
    box.set_facecolor(Y_LIGHT); box.set_edgecolor(Y_MID)
ax.set_xticklabels(labels_box, rotation=35, ha="right", fontsize=7.5, color=MUTED)
ax.axhline(0, color=MUTED, linewidth=1, alpha=0.4, linestyle="--")
ax.set_ylabel("Retorno Diário (%)")
ax.set_title("Boxplot de Retornos — Últimos 12 Meses")
ax.spines["bottom"].set_color(BORDER)

plt.tight_layout(pad=2.5)
plt.savefig("petr4_retornos.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("Salvo: petr4_retornos.png")
print("Todos os graficos gerados!")
