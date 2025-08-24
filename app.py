import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import AverageTrueRange
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# **Configuração da página**
st.set_page_config(
    page_title="📊 Screener Avançado de Ações",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# **CSS personalizado para design moderno**
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4037 0%, #99f2c8 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-left: 4px solid #1f4037;
        margin: 1rem 0;
    }
    
    .signal-compra-forte {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        display: inline-block;
    }
    
    .signal-compra {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        display: inline-block;
    }
    
    .signal-neutro {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        display: inline-block;
    }
    
    .signal-venda {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        display: inline-block;
    }
    
    .signal-venda-forte {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        display: inline-block;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #1f4037 0%, #99f2c8 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

class ScreenerAvancado:
    """Sistema de screener com análise técnica e fundamentalista"""
    
    def __init__(self):
        self.criterios_pesos = {
            'tendencia_ema': 0.25,
            'rsi': 0.20,
            'macd': 0.15,
            'pe_ratio': 0.20,
            'roe': 0.15,
            'liquidez': 0.05
        }
    
    @st.cache_data(ttl=1800)  # Cache por 30 minutos
    def obter_dados_acao(_self, ticker, periodo="1y"):
        """Obtém dados históricos e fundamentais"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=periodo, auto_adjust=True)
            info = stock.info
            
            if hist.empty or len(hist) < 50:
                return None, None
            
            return hist, info
        except Exception as e:
            st.error(f"Erro ao obter dados para {ticker}: {str(e)}")
            return None, None
    
    def calcular_indicadores(self, df):
        """Calcula indicadores técnicos"""
        df = df.copy()
        
        # EMAs
        for periodo in [9, 21, 50, 200]:
            df[f'EMA_{periodo}'] = EMAIndicator(df['Close'], window=periodo).ema_indicator()
        
        # RSI
        df['RSI'] = RSIIndicator(df['Close'], window=14).rsi()
        
        # MACD
        macd = MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Histogram'] = macd.macd_diff()
        
        # ATR
        df['ATR'] = AverageTrueRange(df['High'], df['Low'], df['Close'], window=14).average_true_range()
        
        return df
    
    def avaliar_acao(self, ticker):
        """Avalia uma ação com base nos critérios definidos"""
        df, info = self.obter_dados_acao(ticker)
        
        if df is None or info is None:
            return None
        
        df = self.calcular_indicadores(df)
        ultimo = df.iloc[-1]
        
        # Inicializar resultado
        resultado = {
            'ticker': ticker,
            'preco': ultimo['Close'],
            'criterios': {},
            'score_total': 0.0,
            'gestao_risco': {}
        }
        
        score_total = 0.0
        
        # **1. Tendência EMA**
        preco = ultimo['Close']
        ema9 = ultimo['EMA_9']
        ema21 = ultimo['EMA_21']
        ema50 = ultimo['EMA_50']
        
        if preco > ema9 > ema21 > ema50:
            ema_score = 1.0
            ema_sinal = "Forte Compra"
        elif preco < ema9 < ema21 < ema50:
            ema_score = -1.0
            ema_sinal = "Forte Venda"
        elif preco > ema21:
            ema_score = 0.5
            ema_sinal = "Compra"
        elif preco < ema21:
            ema_score = -0.5
            ema_sinal = "Venda"
        else:
            ema_score = 0.0
            ema_sinal = "Neutro"
        
        score_total += ema_score * self.criterios_pesos['tendencia_ema']
        resultado['criterios']['tendencia_ema'] = {
            'sinal': ema_sinal,
            'score': ema_score,
            'detalhes': f"Preço: ${preco:.2f} | EMA9: ${ema9:.2f}"
        }
        
        # **2. RSI**
        rsi = ultimo['RSI']
        if rsi < 30:
            rsi_score = 1.0
            rsi_sinal = "Forte Compra"
        elif rsi > 70:
            rsi_score = -1.0
            rsi_sinal = "Forte Venda"
        elif 30 <= rsi <= 45:
            rsi_score = 0.5
            rsi_sinal = "Compra"
        elif 55 <= rsi <= 70:
            rsi_score = -0.5
            rsi_sinal = "Venda"
        else:
            rsi_score = 0.0
            rsi_sinal = "Neutro"
        
        score_total += rsi_score * self.criterios_pesos['rsi']
        resultado['criterios']['rsi'] = {
            'sinal': rsi_sinal,
            'score': rsi_score,
            'valor': rsi
        }
        
        # **3. MACD**
        macd_line = ultimo['MACD']
        macd_signal = ultimo['MACD_Signal']
        macd_hist = ultimo['MACD_Histogram']
        
        if macd_line > macd_signal and macd_hist > 0:
            macd_score = 1.0
            macd_sinal = "Compra"
        elif macd_line < macd_signal and macd_hist < 0:
            macd_score = -1.0
            macd_sinal = "Venda"
        else:
            macd_score = 0.0
            macd_sinal = "Neutro"
        
        score_total += macd_score * self.criterios_pesos['macd']
        resultado['criterios']['macd'] = {
            'sinal': macd_sinal,
            'score': macd_score
        }
        
        # **4. P/E Ratio**
        pe_ratio = info.get('trailingPE', None)
        if pe_ratio and pe_ratio > 0:
            if 8 <= pe_ratio <= 18:
                pe_score = 1.0
                pe_sinal = "Compra"
            elif pe_ratio > 30:
                pe_score = -1.0
                pe_sinal = "Venda"
            else:
                pe_score = 0.0
                pe_sinal = "Neutro"
        else:
            pe_score = 0.0
            pe_sinal = "Sem Dados"
            pe_ratio = "N/A"
        
        score_total += pe_score * self.criterios_pesos['pe_ratio']
        resultado['criterios']['pe_ratio'] = {
            'sinal': pe_sinal,
            'score': pe_score,
            'valor': pe_ratio
        }
        
        # **5. ROE**
        roe = info.get('returnOnEquity', None)
        if roe and roe > 0:
            roe_pct = roe * 100
            if roe_pct >= 15:
                roe_score = 1.0
                roe_sinal = "Compra"
            elif roe_pct < 8:
                roe_score = -1.0
                roe_sinal = "Venda"
            else:
                roe_score = 0.0
                roe_sinal = "Neutro"
        else:
            roe_score = 0.0
            roe_sinal = "Sem Dados"
            roe_pct = "N/A"
        
        score_total += roe_score * self.criterios_pesos['roe']
        resultado['criterios']['roe'] = {
            'sinal': roe_sinal,
            'score': roe_score,
            'valor': roe_pct if roe_pct != "N/A" else "N/A"
        }
        
        # **6. Liquidez**
        volume_medio = df['Volume'].tail(20).mean()
        if volume_medio >= 1000000:
            liq_score = 0.5
            liq_sinal = "Alta"
        elif volume_medio >= 100000:
            liq_score = 0.0
            liq_sinal = "Média"
        else:
            liq_score = -0.5
            liq_sinal = "Baixa"
        
        score_total += liq_score * self.criterios_pesos['liquidez']
        resultado['criterios']['liquidez'] = {
            'sinal': liq_sinal,
            'score': liq_score,
            'volume_medio': volume_medio
        }
        
        # **Decisão final**
        resultado['score_total'] = score_total
        
        if score_total >= 0.6:
            resultado['decisao'] = "Forte Compra"
        elif score_total >= 0.2:
            resultado['decisao'] = "Compra"
        elif score_total <= -0.6:
            resultado['decisao'] = "Forte Venda"
        elif score_total <= -0.2:
            resultado['decisao'] = "Venda"
        else:
            resultado['decisao'] = "Neutro"
        
        # **Gestão de risco**
        atr = ultimo['ATR']
        stop_loss = preco - (2.5 * atr)
        volatilidade_pct = (atr / preco) * 100
        
        resultado['gestao_risco'] = {
            'stop_loss': stop_loss,
            'atr': atr,
            'volatilidade_pct': volatilidade_pct,
            'volume_medio': volume_medio
        }
        
        return resultado
    
    def executar_screener(self, tickers):
        """Executa o screener para lista de tickers"""
        resultados = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, ticker in enumerate(tickers):
            status_text.text(f"Analisando {ticker}...")
            progress_bar.progress((i + 1) / len(tickers))
            
            resultado = self.avaliar_acao(ticker)
            if resultado:
                resultados.append(resultado)
        
        progress_bar.empty()
        status_text.empty()
        
        return sorted(resultados, key=lambda x: x['score_total'], reverse=True)

def criar_grafico_tecnico(ticker, df):
    """Cria gráfico técnico com indicadores"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f'{ticker} - Preço e EMAs', 'RSI (14)', 'MACD'),
        row_heights=[0.6, 0.2, 0.2]
    )
    
    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Preço'
        ),
        row=1, col=1
    )
    
    # EMAs
    cores = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    for i, periodo in enumerate([9, 21, 50, 200]):
        if f'EMA_{periodo}' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[f'EMA_{periodo}'],
                    mode='lines',
                    name=f'EMA {periodo}',
                    line=dict(color=cores[i], width=1.5)
                ),
                row=1, col=1
            )
    
    # RSI
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['RSI'],
            mode='lines',
            name='RSI',
            line=dict(color='purple')
        ),
        row=2, col=1
    )
    
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    # MACD
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MACD'],
            mode='lines',
            name='MACD',
            line=dict(color='blue')
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MACD_Signal'],
            mode='lines',
            name='Signal',
            line=dict(color='red')
        ),
        row=3, col=1
    )
    
    colors = ['green' if x >= 0 else 'red' for x in df['MACD_Histogram']]
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['MACD_Histogram'],
            name='Histogram',
            marker_color=colors,
            opacity=0.6
        ),
        row=3, col=1
    )
    
    fig.update_layout(
        height=700,
        showlegend=True,
        template="plotly_white"
    )
    
    return fig

def formatar_sinal_html(decisao):
    """Formata o sinal com CSS apropriado"""
    classes = {
        "Forte Compra": "signal-compra-forte",
        "Compra": "signal-compra",
        "Neutro": "signal-neutro",
        "Venda": "signal-venda",
        "Forte Venda": "signal-venda-forte"
    }
    
    classe = classes.get(decisao, "signal-neutro")
    return f'<div class="{classe}">{decisao}</div>'

def main():
    """Função principal da aplicação"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Screener Avançado de Ações</h1>
        <p>Sistema Inteligente com Análise Técnica e Fundamentalista</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configurações do Screener")
        
        # Tickers input
        tickers_input = st.text_area(
            "📊 Tickers para Análise (separados por vírgula):",
            value="AAPL,MSFT,GOOGL,AMZN,TSLA,META,NVDA,NFLX,JPM,V",
            height=120
        )
        
        # Filtros
        st.markdown("### 🔧 Filtros Opcionais")
        min_volume = st.number_input("Volume mínimo diário:", value=100000, step=50000)
        min_price = st.number_input("Preço mínimo ($):", value=5.0, step=1.0)
        
        # Botão principal
        executar = st.button("🎯 Executar Screener", type="primary")
    
    # Explicação dos critérios
    with st.expander("📚 Como Funciona o Screener"):
        st.markdown("""
        **Sistema de Pontuação Ponderada:**
        
        **Critérios Técnicos (60%):**
        - **Tendência EMA (25%):** Alinhamento das médias móveis exponenciais 9, 21, 50
        - **RSI (20%):** Força relativa - identifica sobrecompra/sobrevenda
        - **MACD (15%):** Convergência/divergência - confirma mudanças de tendência
        
        **Critérios Fundamentalistas (35%):**
        - **P/E Ratio (20%):** Múltiplo preço/lucro - avalia valorização
        - **ROE (15%):** Retorno sobre patrimônio - eficiência da gestão
        
        **Outros (5%):**
        - **Liquidez (5%):** Volume médio de negociação
        
        **Interpretação dos Sinais:**
        - **Score ≥ 0.6:** Forte Compra 🟢🟢🟢
        - **Score ≥ 0.2:** Compra 🟢🟢
        - **Score ≤ -0.6:** Forte Venda 🔴🔴🔴
        - **Score ≤ -0.2:** Venda 🔴🔴
        - **Outros:** Neutro 🟡
        """)
    
    # Execução principal
    if executar:
        tickers = [t.strip().upper() for t in tickers_input.replace(',', ' ').split() if t.strip()]
        
        if not tickers:
            st.error("❌ Por favor, insira pelo menos um ticker válido.")
            return
        
        screener = ScreenerAvancado()
        
        with st.spinner("🔄 Executando análise..."):
            resultados = screener.executar_screener(tickers)
        
        if not resultados:
            st.error("❌ Não foi possível analisar nenhuma ação. Verifique os tickers.")
            return
        
        # Métricas resumo
        st.markdown("### 📈 Resumo da Análise")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Analisado", len(resultados))
        
        with col2:
            forte_compra = len([r for r in resultados if r['decisao'] == 'Forte Compra'])
            st.metric("Forte Compra", forte_compra)
        
        with col3:
            compra = len([r for r in resultados if r['decisao'] == 'Compra'])
            st.metric("Compra", compra)
        
        with col4:
            venda_total = len([r for r in resultados if 'Venda' in r['decisao']])
            st.metric("Venda/Forte Venda", venda_total)
        
        with col5:
            score_medio = np.mean([r['score_total'] for r in resultados])
            st.metric("Score Médio", f"{score_medio:.2f}")
        
        # Tabela principal
        st.markdown("### 🏆 Ranking de Oportunidades")
        
        # Preparar dados
        dados_tabela = []
        for r in resultados:
            dados_tabela.append({
                'Ticker': r['ticker'],
                'Preço': f"${r['preco']:.2f}",
                'Score': f"{r['score_total']:.2f}",
                'Decisão': r['decisao'],
                'RSI': f"{r['criterios']['rsi']['valor']:.1f}",
                'P/E': f"{r['criterios']['pe_ratio']['valor']}" if r['criterios']['pe_ratio']['valor'] != "N/A" else "N/A",
                'ROE%': f"{r['criterios']['roe']['valor']:.1f}%" if r['criterios']['roe']['valor'] != "N/A" else "N/A",
                'Stop Loss': f"${r['gestao_risco']['stop_loss']:.2f}",
                'Vol. Médio': f"{r['gestao_risco']['volume_medio']:,.0f}"
            })
        
        df_display = pd.DataFrame(dados_tabela)
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Análise detalhada
        st.markdown("### 🔍 Análise Detalhada Individual")
        
        ticker_selecionado = st.selectbox(
            "Selecione uma ação para análise completa:",
            options=[r['ticker'] for r in resultados],
            index=0
        )
        
        resultado_detalhado = next(r for r in resultados if r['ticker'] == ticker_selecionado)
        
        # Layout em colunas
        col_info, col_grafico = st.columns([1, 2])
        
        with col_info:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{ticker_selecionado}</h3>
                <p><strong>Preço Atual:</strong> ${resultado_detalhado['preco']:.2f}</p>
                <p><strong>Score Total:</strong> {resultado_detalhado['score_total']:.2f}</p>
                {formatar_sinal_html(resultado_detalhado['decisao'])}
            </div>
            """, unsafe_allow_html=True)
            
            # Gestão de risco
            st.markdown("#### 🛡️ Gestão de Risco")
            risco = resultado_detalhado['gestao_risco']
            st.markdown(f"""
            - **Stop Loss Sugerido:** ${risco['stop_loss']:.2f}
            - **ATR (14):** {risco['atr']:.2f}
            - **Volatilidade:** {risco['volatilidade_pct']:.1f}%
            - **Volume Médio:** {risco['volume_medio']:,.0f}
            """)
            
            # Critérios detalhados
            st.markdown("#### 📊 Detalhamento dos Critérios")
            for criterio, dados in resultado_detalhado['criterios'].items():
                st.markdown(f"""
                **{criterio.replace('_', ' ').title()}:**
                - Sinal: {dados['sinal']}
                - Score: {dados['score']:.2f}
                """)
                if 'valor' in dados and dados['valor'] != "N/A":
                    st.markdown(f"- Valor: {dados['valor']}")
                st.markdown("---")
        
        with col_grafico:
            # Gráfico técnico
            df_grafico, _ = screener.obter_dados_acao(ticker_selecionado, "6mo")
            if df_grafico is not None:
                df_grafico = screener.calcular_indicadores(df_grafico)
                fig = criar_grafico_tecnico(ticker_selecionado, df_grafico)
                st.plotly_chart(fig, use_container_width=True)
        
        # Distribuição de scores
        st.markdown("### 📊 Distribuição dos Scores")
        scores = [r['score_total'] for r in resultados]
        fig_hist = px.histogram(
            x=scores,
            nbins=15,
            title="Distribuição dos Scores de Análise",
            labels={'x': 'Score Total', 'y': 'Quantidade de Ações'},
            color_discrete_sequence=['#1f4037']
        )
        fig_hist.update_layout(template="plotly_white")
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Download dos resultados
        csv = pd.DataFrame(dados_tabela).to_csv(index=False)
        st.download_button(
            label="📥 Baixar Resultados (CSV)",
            data=csv,
            file_name=f"screener_resultados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
