#!/usr/bin/env python3
"""
Sistema de Screener - Versão Otimizada
Compatível com requirements básicos e avançados
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Imports básicos (sempre disponíveis)
import pandas as pd
import numpy as np
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import AverageTrueRange

# Imports opcionais (verificar disponibilidade)
try:
    import matplotlib.pyplot as plt
    PLOTTING = True
except ImportError:
    PLOTTING = False
    print("⚠️  Matplotlib não encontrado. Gráficos desabilitados.")

try:
    from tqdm import tqdm
    PROGRESS_BAR = True
except ImportError:
    PROGRESS_BAR = False
    print("⚠️  tqdm não encontrado. Barras de progresso desabilitadas.")

try:
    from loguru import logger
    ADVANCED_LOGGING = True
except ImportError:
    import logging as logger
    ADVANCED_LOGGING = False

try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    PARALLEL_PROCESSING = True
except ImportError:
    PARALLEL_PROCESSING = False

class ScreenerRobusto:
    """
    Sistema de screener adaptável aos requirements disponíveis
    """
    
    def __init__(self):
        self.setup_logging()
        self.verificar_dependencias()
        
    def setup_logging(self):
        """Configura logging baseado nas dependências disponíveis"""
        if ADVANCED_LOGGING:
            logger.add("screener.log", rotation="1 day", retention="7 days")
        else:
            logging.basicConfig(level=logging.INFO)
    
    def verificar_dependencias(self):
        """Verifica e reporta status das dependências"""
        deps_status = {
            "Core (pandas, numpy, yfinance, ta)": True,
            "Gráficos (matplotlib)": PLOTTING,
            "Progress bars (tqdm)": PROGRESS_BAR,
            "Logging avançado (loguru)": ADVANCED_LOGGING,
            "Processamento paralelo": PARALLEL_PROCESSING
        }
        
        print("📊 Status das Dependências:")
        for dep, status in deps_status.items():
            emoji = "✅" if status else "❌"
            print(f"   {emoji} {dep}")
    
    def obter_dados_com_retry(self, ticker, max_tentativas=3):
        """Obtém dados com retry automático"""
        for tentativa in range(max_tentativas):
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="2y", auto_adjust=True)
                info = stock.info
                
                if len(hist) < 50:  # Dados insuficientes
                    raise ValueError(f"Dados insuficientes para {ticker}")
                
                return self.adicionar_indicadores(hist), info
                
            except Exception as e:
                if tentativa == max_tentativas - 1:
                    if ADVANCED_LOGGING:
                        logger.error(f"Falha ao obter {ticker} após {max_tentativas} tentativas: {e}")
                    return None, None
                else:
                    import time
                    time.sleep(1)  # Aguardar antes de retry
        
        return None, None
    
    def adicionar_indicadores(self, df):
        """Adiciona indicadores técnicos essenciais"""
        df = df.copy()
        
        try:
            # EMAs essenciais
            for periodo in [9, 21, 50]:
                df[f'ema_{periodo}'] = EMAIndicator(df['Close'], window=periodo).ema_indicator()
            
            # RSI
            df['rsi_14'] = RSIIndicator(df['Close'], window=14).rsi()
            
            # MACD
            macd = MACD(df['Close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_histogram'] = macd.macd_diff()
            
            # ATR para gestão de risco
            df['atr_14'] = AverageTrueRange(df['High'], df['Low'], df['Close'], window=14).average_true_range()
            
        except Exception as e:
            print(f"⚠️  Erro ao calcular indicadores: {e}")
        
        return df
    
    def avaliar_acao(self, ticker):
        """Avalia uma ação individual"""
        df, info = self.obter_dados_com_retry(ticker)
        
        if df is None or info is None:
            return None
        
        # Critérios básicos
        score = 0
        criterios = {}
        
        try:
            # Preço atual
            preco_atual = df['Close'].iloc[-1]
            
            # 1. Critério técnico - Tendência EMA
            ema9 = df['ema_9'].iloc[-1]
            ema21 = df['ema_21'].iloc[-1]
            ema50 = df['ema_50'].iloc[-1]
            
            if preco_atual > ema9 > ema21 > ema50:
                score += 1
                criterios['tendencia_ema'] = {"sinal": "Compra", "forca": "Forte"}
            elif preco_atual < ema9 < ema21 < ema50:
                score -= 1
                criterios['tendencia_ema'] = {"sinal": "Venda", "forca": "Forte"}
            else:
                criterios['tendencia_ema'] = {"sinal": "Neutro", "forca": "Fraca"}
            
            # 2. RSI
            rsi_atual = df['rsi_14'].iloc[-1]
            if rsi_atual < 30:
                score += 0.5
                criterios['rsi'] = {"sinal": "Compra", "valor": rsi_atual}
            elif rsi_atual > 70:
                score -= 0.5
                criterios['rsi'] = {"sinal": "Venda", "valor": rsi_atual}
            else:
                criterios['rsi'] = {"sinal": "Neutro", "valor": rsi_atual}
            
            # 3. Fundamentalista básico
            pe_ratio = info.get('trailingPE', None)
            if pe_ratio and 8 <= pe_ratio <= 20:
                score += 0.5
                criterios['pe_ratio'] = {"sinal": "Compra", "valor": pe_ratio}
            elif pe_ratio and pe_ratio > 30:
                score -= 0.5
                criterios['pe_ratio'] = {"sinal": "Venda", "valor": pe_ratio}
            
            # 4. Volume (liquidez)
            volume_medio = df['Volume'].tail(20).mean()
            if volume_medio < 100000:
                score -= 1  # Penalizar baixa liquidez
                criterios['liquidez'] = {"sinal": "Ruim", "volume_medio": volume_medio}
            else:
                criterios['liquidez'] = {"sinal": "OK", "volume_medio": volume_medio}
            
            # Decisão final
            if score >= 1.5:
                decisao = "Forte Compra"
            elif score >= 0.5:
                decisao = "Compra"
            elif score <= -1.5:
                decisao = "Forte Venda"
            elif score <= -0.5:
                decisao = "Venda"
            else:
                decisao = "Neutro"
            
            # Gestão de risco
            atr = df['atr_14'].iloc[-1]
            stop_loss = preco_atual - (2.5 * atr)
            
            return {
                "ticker": ticker,
                "preco": preco_atual,
                "score": score,
                "decisao": decisao,
                "criterios": criterios,
                "gestao_risco": {
                    "stop_loss_sugerido": stop_loss,
                    "atr_percentual": (atr / preco_atual) * 100
                }
            }
            
        except Exception as e:
            if ADVANCED_LOGGING:
                logger.error(f"Erro ao avaliar {ticker}: {e}")
            return None
    
    def executar_screener(self, tickers, usar_paralelo=True):
        """Executa screener com ou sem processamento paralelo"""
        resultados = []
        
        if usar_paralelo and PARALLEL_PROCESSING:
            return self._executar_paralelo(tickers)
        else:
            return self._executar_sequencial(tickers)
    
    def _executar_sequencial(self, tickers):
        """Execução sequencial (compatibilidade máxima)"""
        resultados = []
        
        if PROGRESS_BAR:
            tickers = tqdm(tickers, desc="Analisando")
        
        for ticker in tickers:
            resultado = self.avaliar_acao(ticker)
            if resultado:
                resultados.append(resultado)
                print(f"✅ {ticker}: {resultado['decisao']} (Score: {resultado['score']:.1f})")
            else:
                print(f"❌ {ticker}: Erro na análise")
        
        return sorted(resultados, key=lambda x: x['score'], reverse=True)
    
    def _executar_paralelo(self, tickers):
        """Execução paralela (requer concurrent.futures)"""
        resultados = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_ticker = {executor.submit(self.avaliar_acao, ticker): ticker for ticker in tickers}
            
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    resultado = future.result(timeout=30)
                    if resultado:
                        resultados.append(resultado)
                        print(f"✅ {ticker}: {resultado['decisao']} (Score: {resultado['score']:.1f})")
                except Exception as e:
                    print(f"❌ {ticker}: {e}")
        
        return sorted(resultados, key=lambda x: x['score'], reverse=True)
    
    def gerar_relatorio_simples(self, resultados, arquivo="relatorio.txt"):
        """Gera relatório em texto simples"""
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(f"RELATÓRIO DE SCREENER - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write("="*60 + "\n\n")
            
            for i, resultado in enumerate(resultados[:20], 1):
                f.write(f"{i:2d}. {resultado['ticker']:6s} | {resultado['decisao']:12s} | ")
                f.write(f"Score: {resultado['score']:5.1f} | ${resultado['preco']:8.2f}\n")
        
        print(f"📄 Relatório salvo em: {arquivo}")

# Função principal
def main():
    """Execução principal do screener"""
    print("🚀 Iniciando Sistema de Screener")
    print("="*50)
    
    # Lista de exemplo - personalize conforme necessário
    tickers_exemplo = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX'
    ]
    
    screener = ScreenerRobusto()
    resultados = screener.executar_screener(tickers_exemplo)
    
    # Mostrar top 5
    print(f"\n🏆 TOP 5 OPORTUNIDADES:")
    print("-" * 50)
    
    for i, resultado in enumerate(resultados[:5], 1):
        emoji = "🟢" if "Compra" in resultado['decisao'] else "🔴" if "Venda" in resultado['decisao'] else "🟡"
        print(f"{i}. {emoji} {resultado['ticker']} - {resultado['decisao']} (Score: {resultado['score']:.1f})")
    
    # Salvar relatório
    screener.gerar_relatorio_simples(resultados)
    
    print(f"\n✅ Análise concluída! {len(resultados)} ações processadas.")

if __name__ == "__main__":
    main()
