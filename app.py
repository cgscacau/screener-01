import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import AverageTrueRange, BollingerBands
from datetime import datetime, timedelta
import json
import warnings
from streamlit_option_menu import option_menu
import math
import textwrap

warnings.filterwarnings('ignore')

# **Configuração da página**
st.set_page_config(
    page_title="🇧🇷 Screener Pro BR v2.1.3",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# **CSS Profissional com Tema Escuro**
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
        color: #e2e8f0;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #059669 50%, #d97706 100%);
        padding: 3rem 2rem;
        border-radius: 25px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.4);
        border: 2px solid rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 3.2rem;
        font-weight: 800;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
        background: linear-gradient(45deg, #ffffff, #f0f9ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        margin: 1rem 0 0 0;
        opacity: 0.95;
        font-size: 1.3rem;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }
    
    .opportunity-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
        color: #e2e8f0;
    }
    
    .opportunity-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 60px rgba(59, 130, 246, 0.2);
        border-color: rgba(59, 130, 246, 0.6);
    }
    
    .opportunity-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #10b981, #f59e0b);
        border-radius: 20px 20px 0 0;
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    .ticker-info h3 {
        font-size: 1.8rem;
        font-weight: 700;
        color: #3b82f6;
        margin: 0 0 0.5rem 0;
    }
    
    .company-name {
        font-size: 0.95rem;
        color: #94a3b8;
        font-weight: 400;
        margin-bottom: 1rem;
    }
    
    .price-info {
        text-align: right;
    }
    
    .current-price {
        font-size: 2rem;
        font-weight: 700;
        color: #10b981;
        margin: 0 0 0.3rem 0;
    }
    
    .score-badge {
        background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
        color: #e2e8f0;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    
    .signal-forte-compra {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        padding: 0.8rem 1.8rem;
        border-radius: 30px;
        font-weight: 800;
        font-size: 1rem;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 2px solid rgba(16, 185, 129, 0.3);
        display: inline-block;
        margin: 1rem 0;
    }
    
    .signal-compra {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
        color: white;
        padding: 0.8rem 1.8rem;
        border-radius: 30px;
        font-weight: 800;
        font-size: 1rem;
        box-shadow: 0 8px 25px rgba(52, 211, 153, 0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 2px solid rgba(52, 211, 153, 0.3);
        display: inline-block;
        margin: 1rem 0;
    }
    
    .signal-neutro {
        background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
        color: white;
        padding: 0.8rem 1.8rem;
        border-radius: 30px;
        font-weight: 800;
        font-size: 1rem;
        box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 2px solid rgba(245, 158, 11, 0.3);
        display: inline-block;
        margin: 1rem 0;
    }
    
    .signal-venda {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: white;
        padding: 0.8rem 1.8rem;
        border-radius: 30px;
        font-weight: 800;
        font-size: 1rem;
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 2px solid rgba(239, 68, 68, 0.3);
        display: inline-block;
        margin: 1rem 0;
    }
    
    .signal-forte-venda {
        background: linear-gradient(135deg, #991b1b 0%, #dc2626 100%);
        color: white;
        padding: 0.8rem 1.8rem;
        border-radius: 30px;
        font-weight: 800;
        font-size: 1rem;
        box-shadow: 0 8px 25px rgba(220, 38, 38, 0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 2px solid rgba(220, 38, 38, 0.3);
        display: inline-block;
        margin: 1rem 0;
    }
    
    .strategy-section {
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    
    .strategy-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .strategy-item {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .strategy-item:hover {
        border-color: rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
    }
    
    .strategy-label {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 500;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .strategy-value {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    
    .entry-value { color: #3b82f6; }
    .stop-value { color: #ef4444; }
    .target-value { color: #10b981; }
    
    .strategy-subtitle {
        font-size: 0.75rem;
        color: #64748b;
        font-weight: 400;
    }
    
    .criteria-section {
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    
    .criteria-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .criteria-item {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(100, 116, 139, 0.3);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .criteria-item:hover {
        border-color: rgba(59, 130, 246, 0.4);
    }
    
    .criteria-name {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-bottom: 0.5rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .criteria-signal {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    
    .criteria-value {
        font-size: 0.75rem;
        color: #64748b;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid rgba(59, 130, 246, 0.2);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        margin: 1rem 0;
        color: #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 50px rgba(59, 130, 246, 0.15);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 1rem 3rem;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(30, 58, 138, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: 2px solid rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(30, 58, 138, 0.5);
        background: linear-gradient(135deg, #059669 0%, #1e3a8a 100%);
    }
    
    .info-box, .success-box, .warning-box {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: #e2e8f0;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    .success-box {
        border-left: 4px solid #10b981;
    }
    
    .warning-box {
        border-left: 4px solid #f59e0b;
    }
    
    .info-box {
        border-left: 4px solid #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# **Inicialização do Session State**
def init_session_state():
    """Inicializa variáveis de sessão"""
    if 'screener_executed' not in st.session_state:
        st.session_state.screener_executed = False
    if 'filtered_results' not in st.session_state:
        st.session_state.filtered_results = []
    if 'selected_ticker_analysis' not in st.session_state:
        st.session_state.selected_ticker_analysis = None

# Executar inicialização
init_session_state()

class GerenciadorAtivos:
    """Gerenciador de base de dados de ativos"""
    
    def __init__(self, arquivo_db="assets_database.json"):
        self.arquivo_db = arquivo_db
        self.dados = self.carregar_dados()
    
    def carregar_dados(self):
        """Carrega dados do arquivo JSON"""
        try:
            with open(self.arquivo_db, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.criar_base_inicial()
    
    def salvar_dados(self):
        """Salva dados no arquivo JSON"""
        with open(self.arquivo_db, 'w', encoding='utf-8') as f:
            json.dump(self.dados, f, ensure_ascii=False, indent=2)
    
    def criar_base_inicial(self):
        """Cria base inicial de dados expandida"""
        dados_iniciais = {
            "acoes_brasileiras": {
                "nome": "🇧🇷 Ações Brasileiras (B3)",
                "descricao": "Principais ações da Bolsa Brasileira",
                "tickers": [
                    "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA",
                    "WEGE3.SA", "MGLU3.SA", "ELET3.SA", "SUZB3.SA", "RENT3.SA",
                    "LREN3.SA", "JBSS3.SA", "BBAS3.SA", "ITSA4.SA", "BRDT3.SA",
                    "RADL3.SA", "CCRO3.SA", "RAIL3.SA", "CSAN3.SA", "CMIG4.SA"
                ]
            },
            "fiis": {
                "nome": "🏢 Fundos Imobiliários (FIIs)",
                "descricao": "Fundos de Investimento Imobiliário da B3",
                "tickers": [
                    "HGLG11.SA", "XPML11.SA", "VISC11.SA", "BCFF11.SA", "KNRI11.SA",
                    "MXRF11.SA", "HGRE11.SA", "GGRC11.SA", "KNCR11.SA", "HGRU11.SA"
                ]
            },
            "etfs_brasileiros": {
                "nome": "📊 ETFs Brasileiros",
                "descricao": "Exchange Traded Funds da B3",
                "tickers": [
                    "BOVA11.SA", "IVVB11.SA", "SMAL11.SA", "PIBB11.SA", "ISUS11.SA"
                ]
            },
            "acoes_americanas": {
                "nome": "🇺🇸 Ações Americanas",
                "descricao": "Principais ações do mercado americano",
                "tickers": [
                    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX",
                    "BRK-B", "JNJ", "JPM", "V", "PG", "UNH", "MA", "HD", "DIS"
                ]
            },
            "criptomoedas": {
                "nome": "₿ Criptomoedas",
                "descricao": "Principais criptomoedas",
                "tickers": [
                    "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD",
                    "SOL-USD", "DOGE-USD", "DOT-USD", "MATIC-USD", "AVAX-USD"
                ]
            },
            "commodities": {
                "nome": "🥇 Commodities",
                "descricao": "Principais commodities e futuros",
                "tickers": [
                    "GC=F", "SI=F", "CL=F", "NG=F", "HG=F", "ZC=F", "ZS=F", "KC=F"
                ]
            }
        }
        
        self.salvar_dados_iniciais(dados_iniciais)
        return dados_iniciais
    
    def salvar_dados_iniciais(self, dados):
        """Salva dados iniciais no arquivo"""
        with open(self.arquivo_db, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    
    def obter_categorias(self):
        return list(self.dados.keys())
    
    def obter_tickers_categoria(self, categoria):
        return self.dados.get(categoria, {}).get('tickers', [])
    
    def obter_info_categoria(self, categoria):
        return self.dados.get(categoria, {})
    
    def adicionar_ticker(self, categoria, ticker):
        if categoria in self.dados:
            if ticker not in self.dados[categoria]['tickers']:
                self.dados[categoria]['tickers'].append(ticker.upper())
                self.salvar_dados()
                return True
        return False
    
    def remover_ticker(self, categoria, ticker):
        if categoria in self.dados:
            if ticker in self.dados[categoria]['tickers']:
                self.dados[categoria]['tickers'].remove(ticker)
                self.salvar_dados()
                return True
        return False

class EstrategiaNegociacao:
    """Classe para calcular estratégias automáticas de trading"""
    
    @staticmethod
    def calcular_estrategia(df, resultado_analise):
        """Calcula estratégia completa baseada na análise"""
        ultimo = df.iloc[-1]
        preco_atual = ultimo['Close']
        atr = ultimo.get('ATR', preco_atual * 0.02)
        
        # EMAs para contexto
        ema9 = ultimo.get('EMA_9', preco_atual)
        ema21 = ultimo.get('EMA_21', preco_atual)
        ema50 = ultimo.get('EMA_50', preco_atual)
        
        # RSI para timing
        rsi = ultimo.get('RSI', 50)
        
        # Máximas e mínimas recentes
        high_20 = df['High'].tail(20).max()
        low_20 = df['Low'].tail(20).min()
        
        decisao = resultado_analise['decisao']
        
        if 'Compra' in decisao:
            return EstrategiaNegociacao._estrategia_compra(
                preco_atual, atr, ema9, ema21, ema50, rsi, high_20, low_20, decisao
            )
        elif 'Venda' in decisao:
            return EstrategiaNegociacao._estrategia_venda(
                preco_atual, atr, ema9, ema21, ema50, rsi, high_20, low_20, decisao
            )
        else:
            return EstrategiaNegociacao._estrategia_neutra(preco_atual, atr, ema21)
    
    @staticmethod
    def _estrategia_compra(preco, atr, ema9, ema21, ema50, rsi, high_20, low_20, decisao):
        """Estratégia otimizada para compra com verificações robustas"""
        
        # Definir tipo de entrada baseado no contexto
        if abs(preco - ema21) / preco <= 0.02:  # Próximo da EMA21
            tipo_entrada = "Pullback EMA21"
            entrada = max(preco, ema21 * 1.005)
            multiplicador_stop = 2.0
        else:
            tipo_entrada = "Breakout"
            entrada = max(preco * 1.002, high_20 * 1.001)
            multiplicador_stop = 2.2
        
        # Ajustar baseado na força do sinal
        if 'Forte' in decisao:
            multiplicador_alvo = 4.0
            probabilidade = min(85, 60 + (30 - rsi) * 0.8) if rsi < 50 else 75
        else:
            multiplicador_alvo = 3.0
            probabilidade = min(75, 55 + (40 - rsi) * 0.5) if rsi < 50 else 65
        
        # Cálculos finais com verificações de segurança
        stop_loss = entrada - (atr * multiplicador_stop)
        alvo_1 = entrada + (atr * multiplicador_alvo * 0.6)
        alvo_2 = entrada + (atr * multiplicador_alvo)
        
        # **CORREÇÃO: Verificação de divisão por zero e valores válidos**
        if entrada > stop_loss and (entrada - stop_loss) > 0:
            risco_retorno = (alvo_2 - entrada) / (entrada - stop_loss)
        else:
            risco_retorno = 0
        
        return {
            'tipo': 'COMPRA',
            'setup': tipo_entrada,
            'entrada': entrada,
            'stop_loss': stop_loss,
            'alvo_1': alvo_1,
            'alvo_2': alvo_2,
            'risco_retorno': risco_retorno,
            'probabilidade': int(probabilidade),
            'detalhes': f"Entrada: 40% imediato, 35% no pullback, 25% no breakout confirmado"
        }
    
    @staticmethod
    def _estrategia_venda(preco, atr, ema9, ema21, ema50, rsi, high_20, low_20, decisao):
        """Estratégia otimizada para venda com verificações robustas"""
        
        if abs(preco - ema21) / preco <= 0.02:
            tipo_entrada = "Pullback EMA21 (baixa)"
            entrada = min(preco, ema21 * 0.995)
            multiplicador_stop = 2.0
        else:
            tipo_entrada = "Breakdown"
            entrada = min(preco * 0.998, low_20 * 0.999)
            multiplicador_stop = 2.2
        
        if 'Forte' in decisao:
            multiplicador_alvo = 4.0
            probabilidade = min(85, 60 + (rsi - 70) * 0.8) if rsi > 50 else 75
        else:
            multiplicador_alvo = 3.0
            probabilidade = min(75, 55 + (rsi - 60) * 0.5) if rsi > 50 else 65
        
        stop_loss = entrada + (atr * multiplicador_stop)
        alvo_1 = entrada - (atr * multiplicador_alvo * 0.6)
        alvo_2 = entrada - (atr * multiplicador_alvo)
        
        # **CORREÇÃO: Verificação de divisão por zero**
        if stop_loss > entrada and (stop_loss - entrada) > 0:
            risco_retorno = (entrada - alvo_2) / (stop_loss - entrada)
        else:
            risco_retorno = 0
        
        return {
            'tipo': 'VENDA',
            'setup': tipo_entrada,
            'entrada': entrada,
            'stop_loss': stop_loss,
            'alvo_1': alvo_1,
            'alvo_2': alvo_2,
            'risco_retorno': risco_retorno,
            'probabilidade': int(probabilidade),
            'detalhes': f"Venda: 40% imediato, 35% no rally, 25% na quebra confirmada"
        }
    
    @staticmethod
    def _estrategia_neutra(preco, atr, ema21):
        """Estratégia para sinais neutros"""
        return {
            'tipo': 'AGUARDAR',
            'setup': 'Lateral - Aguardar definição',
            'entrada': None,
            'stop_loss': None,
            'alvo_1': preco * 1.03,
            'alvo_2': preco * 0.97,
            'risco_retorno': 0,
            'probabilidade': 50,
            'detalhes': 'Aguardar rompimento da EMA21 ou consolidação'
        }

class ScreenerAvancado:
    """Sistema de screener com estratégias automáticas"""
    
    def __init__(self):
        self.criterios_pesos = {
            'tendencia_ema': 0.25,
            'rsi': 0.20,
            'macd': 0.15,
            'pe_ratio': 0.15,
            'roe': 0.15,
            'liquidez': 0.10
        }
    
    @st.cache_data(ttl=1800, show_spinner=False)
    def obter_dados_acao(_self, ticker, periodo="1y"):
        """Obtém dados históricos e fundamentais com cache"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=periodo, auto_adjust=True, timeout=15)
            info = stock.info
            
            if hist.empty or len(hist) < 50:
                return None, None
            
            return hist, info
        except Exception:
            return None, None
    
    def calcular_indicadores(self, df):
        """Calcula indicadores técnicos completos"""
        df = df.copy()
        
        try:
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
            
            # Bollinger Bands
            bb = BollingerBands(df['Close'], window=20, window_dev=2)
            df['BB_Upper'] = bb.bollinger_hband()
            df['BB_Lower'] = bb.bollinger_lband()
            df['BB_Middle'] = bb.bollinger_mavg()
            
        except Exception as e:
            st.error(f"Erro ao calcular indicadores: {e}")
        
        return df
    
    def avaliar_acao(self, ticker):
        """Avalia uma ação com estratégia completa"""
        df, info = self.obter_dados_acao(ticker)
        
        if df is None or info is None:
            return None
        
        df = self.calcular_indicadores(df)
        ultimo = df.iloc[-1]
        
        # Inicializar resultado
        resultado = {
            'ticker': ticker,
            'nome': info.get('longName', ticker)[:50] + "..." if len(info.get('longName', ticker)) > 50 else info.get('longName', ticker),
            'preco': ultimo['Close'],
            'criterios': {},
            'score_total': 0.0
        }
        
        score_total = 0.0
        
        # **1. Tendência EMA**
        preco = ultimo['Close']
        ema9 = ultimo.get('EMA_9', preco)
        ema21 = ultimo.get('EMA_21', preco)
        ema50 = ultimo.get('EMA_50', preco)
        
        if preco > ema9 > ema21 > ema50:
            ema_score = 1.0
            ema_sinal = "Forte Compra"
        elif preco > ema21:
            ema_score = 0.5
            ema_sinal = "Compra"
        elif preco < ema9 < ema21 < ema50:
            ema_score = -1.0
            ema_sinal = "Forte Venda"
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
            'valor': f"R$ {preco:.2f}"
        }
        
        # **2. RSI**
        rsi = ultimo.get('RSI', 50)
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
            'valor': f"{rsi:.1f}"
        }
        
        # **3. MACD**
        macd_line = ultimo.get('MACD', 0)
        macd_signal = ultimo.get('MACD_Signal', 0)
        macd_hist = ultimo.get('MACD_Histogram', 0)
        
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
            'score': macd_score,
            'valor': f"{macd_line:.4f}"
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
            'valor': f"{pe_ratio:.1f}" if pe_ratio != "N/A" else "N/A"
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
            'valor': f"{roe_pct:.1f}%" if roe_pct != "N/A" else "N/A"
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
            'valor': f"{volume_medio:,.0f}"
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
        
        # **Calcular estratégia automaticamente**
        estrategia = EstrategiaNegociacao.calcular_estrategia(df, resultado)
        resultado['estrategia'] = estrategia
        
        # **Gestão de risco**
        atr = ultimo.get('ATR', 0)
        volatilidade_pct = (atr / preco) * 100 if preco > 0 else 0
        
        resultado['gestao_risco'] = {
            'atr': atr,
            'volatilidade_pct': volatilidade_pct,
            'volume_medio': volume_medio
        }
        
        return resultado
    
    def executar_screener(self, tickers):
        """Executa screener com estratégias"""
        resultados = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, ticker in enumerate(tickers):
            status_text.text(f"🔍 Analisando {ticker} ({i+1}/{len(tickers)})...")
            progress_bar.progress((i + 1) / len(tickers))
            
            resultado = self.avaliar_acao(ticker)
            if resultado:
                resultados.append(resultado)
        
        progress_bar.empty()
        status_text.empty()
        
        return sorted(resultados, key=lambda x: x['score_total'], reverse=True)

def criar_card_oportunidade(resultado):
    """Cria card individual com correção de renderização HTML"""
    
    estrategia = resultado['estrategia']
    
    # **CORREÇÃO: Função robusta para formatação**
    def formatar_preco(valor):
        if valor is None:
            return "N/A"
        try:
            if isinstance(valor, (int, float)) and (math.isnan(valor) or math.isinf(valor)):
                return "N/A"
            return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except (TypeError, ValueError, OverflowError):
            return "N/A"
    
    # Emoji baseado no tipo
    emoji_tipo = {
        'COMPRA': '📈',
        'VENDA': '📉',
        'AGUARDAR': '⏸️'
    }.get(estrategia['tipo'], '⚖️')
    
    # **CORREÇÃO: HTML sem indentação para evitar interpretação como código**
    card_html = f"""
<div class="opportunity-card">
<div class="card-header">
<div class="ticker-info">
<h3>{resultado['ticker']}</h3>
<div class="company-name">{resultado['nome']}</div>
{formatar_sinal_html_avancado(resultado['decisao'])}
</div>
<div class="price-info">
<div class="current-price">{formatar_preco(resultado['preco'])}</div>
<div class="score-badge">Score: {resultado['score_total']:.2f}</div>
</div>
</div>

<div class="strategy-section">
<h4 style="color: #3b82f6; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
{emoji_tipo} {estrategia['setup']}
<span style="background: linear-gradient(135deg, #10b981, #34d399); color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.8rem; margin-left: auto;">
{estrategia.get('probabilidade', 50)}% sucesso
</span>
</h4>

<div class="strategy-grid">
"""
    
    # **ENTRADA - com validação robusta**
    entrada_valor = estrategia.get('entrada')
    if entrada_valor is not None and not (isinstance(entrada_valor, float) and math.isnan(entrada_valor)):
        card_html += f"""
<div class="strategy-item">
<div class="strategy-label">🎯 Entrada</div>
<div class="strategy-value entry-value">{formatar_preco(entrada_valor)}</div>
<div class="strategy-subtitle">Ponto ideal</div>
</div>
"""
    else:
        card_html += f"""
<div class="strategy-item">
<div class="strategy-label">🎯 Entrada</div>
<div class="strategy-value entry-value">Aguardar</div>
<div class="strategy-subtitle">Indefinido</div>
</div>
"""
    
    # **STOP LOSS - com validação robusta**
    stop_valor = estrategia.get('stop_loss')
    if stop_valor is not None and not (isinstance(stop_valor, float) and math.isnan(stop_valor)):
        card_html += f"""
<div class="strategy-item">
<div class="strategy-label">🛡️ Stop Loss</div>
<div class="strategy-value stop-value">{formatar_preco(stop_valor)}</div>
<div class="strategy-subtitle">Proteção</div>
</div>
"""
    else:
        card_html += f"""
<div class="strategy-item">
<div class="strategy-label">🛡️ Stop Loss</div>
<div class="strategy-value stop-value">N/A</div>
<div class="strategy-subtitle">Indefinido</div>
</div>
"""
    
    # **ALVO - com validação robusta**
    alvo_principal = estrategia.get('alvo_2')
    if alvo_principal is None or (isinstance(alvo_principal, float) and math.isnan(alvo_principal)):
        alvo_principal = estrategia.get('alvo_1')

    if alvo_principal is not None and not (isinstance(alvo_principal, float) and math.isnan(alvo_principal)):
        card_html += f"""
<div class="strategy-item">
<div class="strategy-label">🎯 Alvo</div>
<div class="strategy-value target-value">{formatar_preco(alvo_principal)}</div>
<div class="strategy-subtitle">Meta</div>
</div>
"""
    else:
        card_html += f"""
<div class="strategy-item">
<div class="strategy-label">🎯 Alvo</div>
<div class="strategy-value target-value">N/A</div>
<div class="strategy-subtitle">Indefinido</div>
</div>
"""
    
    card_html += f"""
</div>

<div style="margin-top: 1.5rem; padding: 1.5rem; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); border-radius: 12px; border: 1px solid rgba(59, 130, 246, 0.2);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
<span style="color: #94a3b8; font-weight: 500;">Risco/Retorno:</span>
<span style="color: #10b981; font-weight: 700; font-size: 1.1rem;">
1:{estrategia.get('risco_retorno', 0):.1f}
</span>
</div>
<div style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.5;">
<strong style="color: #3b82f6;">Estratégia:</strong><br>
{estrategia['detalhes']}
</div>
</div>

<div class="criteria-section">
<h5 style="color: #94a3b8; margin-bottom: 1rem;">Critérios de Análise</h5>
<div class="criteria-grid">
"""
    
    # Critérios resumidos
    for criterio, dados in resultado['criterios'].items():
        nome_criterio = criterio.replace('_', ' ').title()
        cor_sinal = {
            'Forte Compra': '#10b981',
            'Compra': '#34d399',
            'Neutro': '#f59e0b',
            'Venda': '#ef4444',
            'Forte Venda': '#dc2626',
            'Sem Dados': '#6b7280'
        }.get(dados['sinal'], '#6b7280')
        
        card_html += f"""
<div class="criteria-item">
<div class="criteria-name">{nome_criterio}</div>
<div class="criteria-signal" style="color: {cor_sinal};">{dados['sinal']}</div>
<div class="criteria-value">{dados.get('valor', '')}</div>
</div>
"""
    
    card_html += """
</div>
</div>
</div>
</div>
"""
    
    # **CORREÇÃO: Usar textwrap.dedent para remover indentação**
    return textwrap.dedent(card_html)

def formatar_sinal_html_avancado(decisao):
    """Formata sinais com design avançado"""
    classes = {
        "Forte Compra": "signal-forte-compra",
        "Compra": "signal-compra",
        "Neutro": "signal-neutro",
        "Venda": "signal-venda",
        "Forte Venda": "signal-forte-venda"
    }
    
    emojis = {
        "Forte Compra": "🚀",
        "Compra": "📈",
        "Neutro": "⚖️",
        "Venda": "📉",
        "Forte Venda": "💥"
    }
    
    classe = classes.get(decisao, "signal-neutro")
    emoji = emojis.get(decisao, "⚖️")
    
    return f'<div class="{classe}">{emoji} {decisao}</div>'

def criar_grafico_profissional(ticker, df):
    """Cria gráfico técnico profissional com tema escuro"""
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        subplot_titles=(
            f'{ticker} - Análise Técnica Completa',
            'RSI (14)',
            'MACD',
            'Volume'
        ),
        row_heights=[0.5, 0.2, 0.2, 0.1]
    )
    
    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Preço',
            increasing_line_color='#10b981',
            decreasing_line_color='#ef4444',
            increasing_fillcolor='rgba(16, 185, 129, 0.3)',
            decreasing_fillcolor='rgba(239, 68, 68, 0.3)'
        ),
        row=1, col=1
    )
    
    # Bollinger Bands
    if 'BB_Upper' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_Upper'],
                mode='lines',
                name='BB Superior',
                line=dict(color='#8b5cf6', width=1, dash='dash'),
                opacity=0.6
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_Lower'],
                mode='lines',
                name='BB Inferior',
                line=dict(color='#8b5cf6', width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(139, 92, 246, 0.1)',
                opacity=0.6
            ),
            row=1, col=1
        )
    
    # EMAs
    ema_config = [
        (9, '#3b82f6', 2),
        (21, '#f59e0b', 2),
        (50, '#ef4444', 2),
        (200, '#8b5cf6', 3)
    ]
    
    for periodo, cor, largura in ema_config:
        if f'EMA_{periodo}' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[f'EMA_{periodo}'],
                    mode='lines',
                    name=f'EMA {periodo}',
                    line=dict(color=cor, width=largura),
                    opacity=0.8
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
            line=dict(color='#06b6d4', width=2)
        ),
        row=2, col=1
    )
    
    fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", opacity=0.7, row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#10b981", opacity=0.7, row=2, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="#6b7280", opacity=0.5, row=2, col=1)
    
    # MACD
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MACD'],
            mode='lines',
            name='MACD',
            line=dict(color='#3b82f6', width=2)
        ),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['MACD_Signal'],
            mode='lines',
            name='Signal',
            line=dict(color='#ef4444', width=2)
        ),
        row=3, col=1
    )
    
    # Histograma MACD
    colors = ['#10b981' if x >= 0 else '#ef4444' for x in df['MACD_Histogram']]
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['MACD_Histogram'],
            name='Histogram',
            marker_color=colors,
            opacity=0.7
        ),
        row=3, col=1
    )
    
    # Volume
    volume_colors = ['#10b981' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ef4444' 
                     for i in range(len(df))]
    
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=volume_colors,
            opacity=0.8
        ),
        row=4, col=1
    )
    
    # Layout profissional escuro
    fig.update_layout(
        height=900,
        showlegend=True,
        template="plotly_dark",
        title_x=0.5,
        font=dict(family="Inter", size=12, color="#e2e8f0"),
        plot_bgcolor='#0f172a',
        paper_bgcolor='#1e293b',
        xaxis_rangeslider_visible=False
    )
    
    # Atualizar eixos
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
    
    return fig

def main():
    """Função principal da aplicação corrigida"""
    
    # Header brasileiro refinado
    st.markdown("""
    <div class="main-header">
        <h1>🇧🇷 Screener Pro BR v2.1.3</h1>
        <p>Sistema Avançado com Estratégias Automáticas - Problemas Corrigidos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar gerenciadores
    gerenciador_ativos = GerenciadorAtivos()
    screener = ScreenerAvancado()
    
    # Menu principal
    selected = option_menu(
        menu_title=None,
        options=["🎯 Screener", "📊 Gerenciar Ativos", "📚 Estratégias"],
        icons=["search", "gear", "book"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#3b82f6", "font-size": "20px"},
            "nav-link": {"font-size": "18px", "text-align": "center", "margin": "0px", 
                        "--hover-color": "rgba(59, 130, 246, 0.1)", "color": "#e2e8f0"},
            "nav-link-selected": {"background-color": "rgba(59, 130, 246, 0.2)", "color": "white"},
        }
    )
    
    if selected == "🎯 Screener":
        # **PÁGINA PRINCIPAL - SCREENER**
        
        # Sidebar
        with st.sidebar:
            st.markdown("### ⚙️ Configurações do Screener")
            
            # Seleção de categoria
            categorias = gerenciador_ativos.obter_categorias()
            categoria_opcoes = {}
            
            for cat in categorias:
                info = gerenciador_ativos.obter_info_categoria(cat)
                categoria_opcoes[info.get('nome', cat)] = cat
            
            categoria_selecionada_nome = st.selectbox(
                "📂 Categoria de Ativos:",
                options=list(categoria_opcoes.keys()),
                index=0
            )
            
            categoria_selecionada = categoria_opcoes[categoria_selecionada_nome]
            info_categoria = gerenciador_ativos.obter_info_categoria(categoria_selecionada)
            
            st.markdown(f"""
            <div class="info-box">
                <strong>{info_categoria.get('nome', 'Categoria')}</strong><br>
                <small>{info_categoria.get('descricao', 'Sem descrição')}</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Tickers da categoria
            tickers_categoria = gerenciador_ativos.obter_tickers_categoria(categoria_selecionada)
            
            # Seleção de tickers
            tickers_selecionados = st.multiselect(
                f"📊 Ativos para Análise ({len(tickers_categoria)} disponíveis):",
                options=tickers_categoria,
                default=tickers_categoria[:8] if len(tickers_categoria) > 8 else tickers_categoria
            )
            
            # Ticker personalizado
            st.markdown("---")
            st.markdown("### ➕ Ticker Personalizado")
            ticker_personalizado = st.text_input("Adicionar:", placeholder="Ex: PETR4.SA")
            
            if st.button("Incluir na Análise") and ticker_personalizado:
                if ticker_personalizado.upper() not in tickers_selecionados:
                    tickers_selecionados.append(ticker_personalizado.upper())
                    st.success(f"✅ {ticker_personalizado.upper()} incluído!")
            
            # Filtros
            st.markdown("---")
            st.markdown("### 🔧 Filtros")
            
            col1, col2 = st.columns(2)
            with col1:
                min_volume = st.number_input("Vol. mín. (K):", value=100, step=50)
                min_score = st.slider("Score mín.:", -3.0, 3.0, -0.5, 0.1)
            
            with col2:
                max_pe = st.number_input("P/E máx.:", value=30, step=5)
                apenas_compra = st.checkbox("Apenas sinais de compra")
            
            # Botão principal
            st.markdown("---")
            executar = st.button("🚀 Executar Análise Completa", type="primary")
        
        # **CORREÇÃO: Lógica de execução com session_state**
        if executar:
            # Resetar estado e executar nova análise
            st.session_state.screener_executed = False
            st.session_state.filtered_results = []
            
            if not tickers_selecionados:
                st.error("❌ Selecione pelo menos um ativo!")
                return
            
            st.markdown(f"""
            <div class="success-box">
                <strong>🔍 Analisando {len(tickers_selecionados)} ativos...</strong><br>
                Categoria: {info_categoria.get('nome')}<br>
                Filtros: Volume mín. {min_volume}K, Score mín. {min_score}
            </div>
            """, unsafe_allow_html=True)
            
            # Executar screener
            with st.spinner("🔄 Processando análise com estratégias..."):
                resultados = screener.executar_screener(tickers_selecionados)
            
            if not resultados:
                st.error("❌ Não foi possível analisar nenhum ativo.")
                return
            
            # Aplicar filtros
            resultados_filtrados = []
            for r in resultados:
                volume_ok = r['gestao_risco']['volume_medio'] >= (min_volume * 1000)
                score_ok = r['score_total'] >= min_score
                
                pe_ok = True
                if r['criterios']['pe_ratio']['valor'] != 'N/A':
                    try:
                        pe_ok = float(r['criterios']['pe_ratio']['valor']) <= max_pe
                    except:
                        pe_ok = True
                
                compra_ok = True
                if apenas_compra:
                    compra_ok = 'Compra' in r['decisao']
                
                if volume_ok and score_ok and pe_ok and compra_ok:
                    resultados_filtrados.append(r)
            
            # **CORREÇÃO: Salvar no session_state**
            st.session_state.filtered_results = resultados_filtrados
            st.session_state.screener_executed = True
            
            # Definir ticker padrão para análise
            if resultados_filtrados:
                st.session_state.selected_ticker_analysis = resultados_filtrados[0]['ticker']
        
        # **Exibir resultados se existirem no session_state**
        if st.session_state.screener_executed and st.session_state.filtered_results:
            resultados_filtrados = st.session_state.filtered_results
            
            st.success(f"✅ {len(resultados_filtrados)} oportunidades identificadas!")
            
            if not resultados_filtrados:
                st.warning("⚠️ Nenhum ativo passou nos filtros.")
                return
            
            # **DASHBOARD**
            st.markdown("### 📊 Dashboard Executivo")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("📈 Analisados", len(resultados_filtrados))
            
            with col2:
                forte_compra = len([r for r in resultados_filtrados if r['decisao'] == 'Forte Compra'])
                st.metric("🚀 Forte Compra", forte_compra)
            
            with col3:
                compra = len([r for r in resultados_filtrados if r['decisao'] == 'Compra'])
                st.metric("📈 Compra", compra)
            
            with col4:
                rr_values = [r['estrategia'].get('risco_retorno', 0) for r in resultados_filtrados if r['estrategia'].get('risco_retorno', 0) > 0]
                rr_medio = np.mean(rr_values) if rr_values else 0
                st.metric("⚖️ R/R Médio", f"1:{rr_medio:.1f}" if rr_medio > 0 else "N/A")
            
            with col5:
                prob_media = np.mean([r['estrategia'].get('probabilidade', 50) for r in resultados_filtrados])
                st.metric("🎯 Prob. Média", f"{prob_media:.0f}%")
            
            # **OPORTUNIDADES COM CARDS COMPLETOS - CORREÇÃO APLICADA**
            st.markdown("### 🏆 Oportunidades com Estratégias Completas")
            
            # **CORREÇÃO: Renderizar cards com unsafe_allow_html=True**
            for resultado in resultados_filtrados[:10]:  # Top 10
                st.markdown(criar_card_oportunidade(resultado), unsafe_allow_html=True)
            
            # **ANÁLISE TÉCNICA DETALHADA - CORREÇÃO DO RESET**
            st.markdown("---")
            st.markdown("### 🔍 Análise Técnica Detalhada")
            
            # **CORREÇÃO: Selectbox com key única e persistência**
            tickers_disponiveis = [r['ticker'] for r in resultados_filtrados]
            
            # Verificar se o ticker selecionado ainda está disponível
            if st.session_state.selected_ticker_analysis not in tickers_disponiveis:
                st.session_state.selected_ticker_analysis = tickers_disponiveis[0]
            
            ticker_detalhado = st.selectbox(
                "Selecione um ativo para gráfico técnico:",
                options=tickers_disponiveis,
                index=tickers_disponiveis.index(st.session_state.selected_ticker_analysis),
                key="selectbox_analise_tecnica"
            )
            
            # Atualizar session_state
            st.session_state.selected_ticker_analysis = ticker_detalhado
            
            # Gráfico técnico
            if ticker_detalhado:
                with st.spinner(f"Carregando análise técnica de {ticker_detalhado}..."):
                    df_grafico, _ = screener.obter_dados_acao(ticker_detalhado, "6mo")
                    if df_grafico is not None and len(df_grafico) > 50:
                        df_grafico = screener.calcular_indicadores(df_grafico)
                        fig = criar_grafico_profissional(ticker_detalhado, df_grafico)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error(f"❌ Não foi possível carregar dados para {ticker_detalhado}.")
            
            # **EXPORT**
            st.markdown("---")
            st.markdown("### 💾 Exportar Resultados")
            
            # Preparar dados
            dados_export = []
            for r in resultados_filtrados:
                estrategia = r['estrategia']
                dados_export.append({
                    'Ticker': r['ticker'],
                    'Nome': r['nome'],
                    'Preço': r['preco'],
                    'Score': r['score_total'],
                    'Decisão': r['decisao'],
                    'Setup': estrategia['setup'],
                    'Entrada': estrategia.get('entrada'),
                    'Stop Loss': estrategia.get('stop_loss'),
                    'Alvo': estrategia.get('alvo_2'),
                    'R/R': estrategia.get('risco_retorno', 0),
                    'Probabilidade': estrategia.get('probabilidade', 50)
                })
            
            col_exp1, col_exp2, col_exp3 = st.columns(3)
            
            with col_exp1:
                csv_completo = pd.DataFrame(dados_export).to_csv(index=False)
                st.download_button(
                    label="📥 Download Completo (CSV)",
                    data=csv_completo,
                    file_name=f"screener_estrategias_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
            
            with col_exp2:
                forte_compra_data = [d for d in dados_export if d['Decisão'] == 'Forte Compra']
                if forte_compra_data:
                    csv_forte_compra = pd.DataFrame(forte_compra_data).to_csv(index=False)
                    st.download_button(
                        label="🚀 Apenas Forte Compra",
                        data=csv_forte_compra,
                        file_name=f"forte_compra_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
            
            with col_exp3:
                resumo = f"""
SCREENER PRO BR v2.1.3 - RELATÓRIO CORRIGIDO
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

CORREÇÕES IMPLEMENTADAS:
✅ HTML renderizado corretamente
✅ Sem reset da tela ao selecionar ativo
✅ Tratamento robusto de valores NaN
✅ Verificações matemáticas de segurança

RESUMO:
- Analisados: {len(resultados_filtrados)}
- Forte Compra: {forte_compra}
- R/R médio: 1:{rr_medio:.1f}
- Probabilidade média: {prob_media:.0f}%

TOP 5:
{chr(10).join([f"{i+1}. {r['ticker']} - {r['decisao']} (R/R: 1:{r['estrategia'].get('risco_retorno', 0):.1f})" for i, r in enumerate(resultados_filtrados[:5])])}
                """
                
                st.download_button(
                    label="📄 Relatório Corrigido",
                    data=resumo,
                    file_name=f"relatorio_corrigido_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )
            
            # Botão para nova análise
            st.markdown("---")
            if st.button("🔄 Nova Análise", type="secondary"):
                st.session_state.screener_executed = False
                st.session_state.filtered_results = []
                st.session_state.selected_ticker_analysis = None
                st.rerun()
                
        elif not st.session_state.screener_executed:
            # Página inicial
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                st.markdown("""
                <div class="success-box" style="text-align: center; padding: 4rem 2rem;">
                    <h2 style="margin-bottom: 2rem;">🎯 Screener Pro BR v2.1.3</h2>
                    <p style="font-size: 1.2rem; margin-bottom: 2rem;">
                        <strong>Versão Corrigida</strong> - Todos os problemas resolvidos
                    </p>
                    <div style="background: rgba(0,0,0,0.2); padding: 2rem; border-radius: 15px; margin: 2rem 0;">
                        <h3 style="color: #10b981; margin-bottom: 1rem;">✅ Correções v2.1.3:</h3>
                        <div style="text-align: left; display: inline-block;">
                            <p>🔧 <strong>HTML renderizado corretamente (textwrap.dedent)</strong></p>
                            <p>🔒 <strong>Sem reset da tela (st.session_state)</strong></p>
                            <p>🛡️ <strong>Tratamento robusto de NaN/None</strong></p>
                            <p>⚖️ <strong>Verificações matemáticas de segurança</strong></p>
                            <p>🎯 <strong>Estratégias completas visíveis</strong></p>
                            <p>📈 <strong>Interface estável e profissional</strong></p>
                        </div>
                    </div>
                    <p style="margin-top: 2rem; opacity: 0.8;">
                        Selecione os ativos na barra lateral e execute a análise
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    elif selected == "📊 Gerenciar Ativos":
        # **GERENCIAMENTO DE ATIVOS** (mantém código original)
        
        st.markdown("### 📊 Gerenciamento de Watchlists")
        
        tab1, tab2 = st.tabs(["📝 Editar Listas", "📋 Visualizar Todas"])
        
        with tab1:
            categorias = gerenciador_ativos.obter_categorias()
            categoria_edit = st.selectbox(
                "Selecione a categoria:",
                options=categorias
            )
            
            if categoria_edit:
                info_cat = gerenciador_ativos.obter_info_categoria(categoria_edit)
                tickers_atuais = gerenciador_ativos.obter_tickers_categoria(categoria_edit)
                
                st.markdown(f"""
                <div class="info-box">
                    <strong>{info_cat.get('nome', categoria_edit)}</strong><br>
                    {info_cat.get('descricao', 'Sem descrição')}<br>
                    <small>Total: {len(tickers_atuais)} ativos</small>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**➕ Adicionar:**")
                    novo_ticker = st.text_input("Ticker:", key=f"add_{categoria_edit}")
                    
                    if st.button("Adicionar", key=f"btn_add_{categoria_edit}"):
                        if novo_ticker:
                            if gerenciador_ativos.adicionar_ticker(categoria_edit, novo_ticker):
                                st.success(f"✅ {novo_ticker.upper()} adicionado!")
                                st.rerun()
                
                with col2:
                    st.markdown("**➖ Remover:**")
                    if tickers_atuais:
                        ticker_remover = st.selectbox(
                            "Selecione:",
                            options=tickers_atuais,
                            key=f"remove_{categoria_edit}"
                        )
                        
                        if st.button("Remover", key=f"btn_remove_{categoria_edit}"):
                            if gerenciador_ativos.remover_ticker(categoria_edit, ticker_remover):
                                st.success(f"✅ {ticker_remover} removido!")
                                st.rerun()
                
                # Lista atual
                if tickers_atuais:
                    st.markdown("**📋 Tickers Atuais:**")
                    cols = st.columns(4)
                    for i, ticker in enumerate(tickers_atuais):
                        with cols[i % 4]:
                            st.info(f"**{ticker}**")
        
        with tab2:
            categorias = gerenciador_ativos.obter_categorias()
            
            for categoria in categorias:
                info = gerenciador_ativos.obter_info_categoria(categoria)
                tickers = gerenciador_ativos.obter_tickers_categoria(categoria)
                
                with st.expander(f"{info.get('nome', categoria)} ({len(tickers)} ativos)"):
                    st.markdown(f"**Descrição:** {info.get('descricao', 'Sem descrição')}")
                    
                    if tickers:
                        cols = st.columns(5)
                        for i, ticker in enumerate(tickers):
                            with cols[i % 5]:
                                st.success(f"**{ticker}**")
    
    elif selected == "📚 Estratégias":
        # **GUIA DE ESTRATÉGIAS** (mantém código original)
        
        st.markdown("### 📚 Guia de Estratégias Automáticas")
        
        tab1, tab2, tab3 = st.tabs(["🎯 Estratégias", "📊 Indicadores", "❓ FAQ"])
        
        with tab1:
            st.markdown("""
            ## 🎯 Estratégias Implementadas
            
            ### **Compra - Pullback EMA21** 📈
            **Quando:** Preço próximo da EMA21 + RSI favorável
            - **Entrada:** EMA21 + 0.5%
            - **Stop:** 2.0x ATR
            - **Alvo:** 4.0x ATR
            - **Probabilidade:** 75-85%
            
            ### **Compra - Breakout** 🚀
            **Quando:** Rompimento de máxima + volume
            - **Entrada:** Máxima 20d + 0.1%
            - **Stop:** 2.2x ATR
            - **Alvo:** 3.0-4.0x ATR
            - **Probabilidade:** 65-80%
            
            ### **Venda - Breakdown** 📉
            **Quando:** Quebra de suporte + RSI alto
            - **Entrada:** Mínima 20d - 0.1%
            - **Stop:** 2.2x ATR
            - **Alvo:** 3.0-4.0x ATR
            - **Probabilidade:** 65-80%
            """)
        
        with tab2:
            st.markdown("""
            ## 📊 Indicadores Utilizados
            
            ### **EMAs (25% do peso)**
            - EMA 9, 21, 50, 200
            - Alinhamento = tendência
            
            ### **RSI (20% do peso)**
            - < 30: Oversold (compra)
            - > 70: Overbought (venda)
            - Base para probabilidade
            
            ### **MACD (15% do peso)**
            - Confirmação de momentum
            - Divergências importantes
            
            ### **ATR**
            - Base para stops e alvos
            - Normaliza volatilidade
            """)
        
        with tab3:
            st.markdown("""
            ## ❓ Perguntas Frequentes
            
            **P: Como foram corrigidos os problemas?**
            R: Usamos `textwrap.dedent()` para HTML e `st.session_state` para persistência.
            
            **P: O que é R/R 1:2.5?**
            R: Para cada R$ 1 de risco, potencial de R$ 2,50 de retorno.
            
            **P: Posso confiar 100% nos sinais?**
            R: NÃO! Use como ferramenta de apoio, sempre faça sua análise.
            
            **P: Como calcular tamanho da posição?**
            R: (Capital × 2%) ÷ (Entrada - Stop) = Quantidade
            """)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #1e3a8a 0%, #059669 50%, #d97706 100%); 
                border-radius: 20px; color: white; margin-top: 3rem;">
        <h3>🇧🇷 Screener Pro BR v2.1.3</h3>
        <p>Sistema Profissional com Problemas Corrigidos</p>
        <small style="opacity: 0.8;">v2.1.3 | {datetime.now().strftime('%d/%m/%Y')} | ✅ Totalmente Funcional</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
