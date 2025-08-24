import yfinance as yf
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, MACD, EMAIndicator
from ta.volatility import AverageTrueRange
import json
from datetime import datetime, timedelta

class ScreenerAvancado:
    def __init__(self, config_file="criterios_config.json"):
        self.config = self.carregar_configuracao(config_file)
        self.historico_sinais = {}
    
    def carregar_configuracao(self, arquivo):
        """Carrega configuração de critérios e pesos"""
        config_padrao = {
            "liquidez": {
                "min_preco": 5.0,
                "min_volume_medio": 500000,
                "min_volume_dolar": 5000000,
                "habilitado": True
            },
            "fundamentalista": {
                "pe_ratio": {"min": 5, "max": 25, "peso": 0.15, "habilitado": True},
                "pb_ratio": {"min": 0.5, "max": 3.0, "peso": 0.10, "habilitado": True},
                "roe": {"min": 10, "max": 50, "peso": 0.15, "habilitado": True}
            },
            "tecnico": {
                "rsi": {"oversold": 30, "overbought": 70, "peso": 0.20, "habilitado": True},
                "macd": {"peso": 0.15, "habilitado": True},
                "ema_trend": {"periodos": [9, 21, 50], "peso": 0.25, "habilitado": True}
            }
        }
        
        try:
            with open(arquivo, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return config_padrao
    
    def obter_dados_completos(self, ticker, periodo="2y"):
        """Obtém dados históricos e fundamentais"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=periodo, auto_adjust=True)
            info = stock.info
            
            # Adicionar indicadores técnicos
            hist = self.adicionar_indicadores(hist)
            
            return hist, info
        except Exception as e:
            print(f"Erro ao obter dados para {ticker}: {e}")
            return None, None
    
    def adicionar_indicadores(self, df):
        """Adiciona indicadores técnicos ao DataFrame"""
        df = df.copy()
        
        # EMAs
        for periodo in [9, 21, 50, 200]:
            df[f'ema_{periodo}'] = EMAIndicator(df['Close'], window=periodo).ema_indicator()
        
        # RSI
        df['rsi_14'] = RSIIndicator(df['Close'], window=14).rsi()
        
        # MACD
        macd = MACD(df['Close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_histogram'] = macd.macd_diff()
        
        # ATR
        df['atr_14'] = AverageTrueRange(df['High'], df['Low'], df['Close'], window=14).average_true_range()
        
        return df
    
    def avaliar_criterio_fundamentalista(self, info, criterio, config):
        """Avalia critérios fundamentalistas"""
        if not config.get('habilitado', False):
            return 0, {"forca": "desabilitado"}
        
        valor = info.get(criterio.replace('_', ''), None)
        if valor is None:
            return 0, {"forca": "sem_dados"}
        
        min_val = config.get('min', 0)
        max_val = config.get('max', float('inf'))
        
        if criterio == 'pe_ratio':
            if 8 <= valor <= 15:
                return 1, {"forca": "forte", "valor": valor}
            elif 15 < valor <= 25:
                return 0, {"forca": "neutro", "valor": valor}
            else:
                return -1, {"forca": "forte", "valor": valor}
        
        elif criterio == 'roe':
            if valor >= 20:
                return 1, {"forca": "forte", "valor": valor}
            elif 10 <= valor < 20:
                return 0, {"forca": "neutro", "valor": valor}
            else:
                return -1, {"forca": "fraco", "valor": valor}
        
        return 0, {"forca": "neutro", "valor": valor}
    
    def avaliar_criterio_tecnico(self, df, criterio, config):
        """Avalia critérios técnicos com força histórica"""
        if not config.get('habilitado', False):
            return 0, {"forca": "desabilitado"}
        
        if len(df) < 200:
            return 0, {"forca": "dados_insuficientes"}
        
        ultimo = df.iloc[-1]
        
        if criterio == 'rsi':
            rsi_atual = ultimo['rsi_14']
            if rsi_atual < 30:
                sinal = 1
            elif rsi_atual > 70:
                sinal = -1
            else:
                sinal = 0
            
            # Avaliar força histórica
            forca_hist = self.avaliar_forca_rsi(df)
            return sinal, forca_hist
        
        elif criterio == 'ema_trend':
            ema9 = ultimo['ema_9']
            ema21 = ultimo['ema_21']
            ema50 = ultimo['ema_50']
            preco = ultimo['Close']
            
            if preco > ema9 > ema21 > ema50:
                sinal = 1
            elif preco < ema9 < ema21 < ema50:
                sinal = -1
            else:
                sinal = 0
            
            forca_hist = self.avaliar_forca_ema_trend(df)
            return sinal, forca_hist
        
        return 0, {"forca": "neutro"}
    
    def avaliar_forca_rsi(self, df, lookback=252*2):
        """Avalia força histórica do RSI"""
        if len(df) < lookback:
            return {"forca": "dados_insuficientes"}
        
        # Eventos de RSI oversold
        eventos_oversold = (df['rsi_14'] < 30).shift(1).fillna(False)
        retornos_5d = df['Close'].pct_change(5).shift(-5)
        retornos_20d = df['Close'].pct_change(20).shift(-20)
        
        sample_5d = retornos_5d[eventos_oversold].dropna()
        sample_20d = retornos_20d[eventos_oversold].dropna()
        
        if len(sample_20d) < 15:
            return {"forca": "poucos_eventos", "n_eventos": len(sample_20d)}
        
        sharpe_20d = sample_20d.mean() / sample_20d.std() if sample_20d.std() > 0 else 0
        taxa_acerto = (sample_20d > 0).mean()
        
        if sharpe_20d > 0.3 and taxa_acerto > 0.6:
            forca = "forte"
        elif sharpe_20d > 0.15 and taxa_acerto > 0.55:
            forca = "moderado"
        else:
            forca = "fraco"
        
        return {
            "forca": forca,
            "sharpe_20d": sharpe_20d,
            "taxa_acerto": taxa_acerto,
            "n_eventos": len(sample_20d),
            "retorno_medio_20d": sample_20d.mean()
        }
    
    def avaliar_forca_ema_trend(self, df):
        """Avalia força histórica da tendência EMA"""
        # Identificar cruzamentos de EMA
        ema9_acima_21 = df['ema_9'] > df['ema_21']
        ema21_acima_50 = df['ema_21'] > df['ema_50']
        
        # Eventos de trend bullish
        trend_bullish = ema9_acima_21 & ema21_acima_50
        mudanca_trend = trend_bullish & ~trend_bullish.shift(1)
        
        retornos_20d = df['Close'].pct_change(20).shift(-20)
        sample = retornos_20d[mudanca_trend].dropna()
        
        if len(sample) < 10:
            return {"forca": "poucos_eventos", "n_eventos": len(sample)}
        
        sharpe = sample.mean() / sample.std() if sample.std() > 0 else 0
        taxa_acerto = (sample > 0).mean()
        
        if sharpe > 0.25 and taxa_acerto > 0.65:
            forca = "forte"
        elif sharpe > 0.1 and taxa_acerto > 0.55:
            forca = "moderado"
        else:
            forca = "fraco"
        
        return {
            "forca": forca,
            "sharpe": sharpe,
            "taxa_acerto": taxa_acerto,
            "n_eventos": len(sample)
        }
    
    def calcular_score_final(self, ticker):
        """Calcula score final combinando todos os critérios"""
        df, info = self.obter_dados_completos(ticker)
        
        if df is None or info is None:
            return None
        
        resultado = {
            "ticker": ticker,
            "preco": df['Close'].iloc[-1],
            "criterios": {},
            "score_total": 0,
            "decisao": "Neutro"
        }
        
        score_total = 0
        peso_total = 0
        
        # Avaliar critérios fundamentalistas
        for criterio, config in self.config.get('fundamentalista', {}).items():
            if config.get('habilitado', False):
                sinal, detalhes = self.avaliar_criterio_fundamentalista(info, criterio, config)
                peso = config.get('peso', 0.1)
                score_total += sinal * peso
                peso_total += peso
                
                resultado['criterios'][criterio] = {
                    "sinal": sinal,
                    "peso": peso,
                    "detalhes": detalhes
                }
        
        # Avaliar critérios técnicos
        for criterio, config in self.config.get('tecnico', {}).items():
            if config.get('habilitado', False):
                sinal, detalhes = self.avaliar_criterio_tecnico(df, criterio, config)
                peso = config.get('peso', 0.1)
                
                # Ajustar peso pela força histórica
                fator_forca = 1.0
                if detalhes.get('forca') == 'forte':
                    fator_forca = 1.3
                elif detalhes.get('forca') == 'fraco':
                    fator_forca = 0.7
                
                score_ajustado = sinal * peso * fator_forca
                score_total += score_ajustado
                peso_total += peso
                
                resultado['criterios'][criterio] = {
                    "sinal": sinal,
                    "peso": peso,
                    "fator_forca": fator_forca,
                    "detalhes": detalhes
                }
        
        # Normalizar score
        if peso_total > 0:
            score_total = score_total / peso_total * 3  # Escalar para range -3 a +3
        
        resultado['score_total'] = score_total
        
        # Determinar decisão
        if score_total >= 2.0:
            resultado['decisao'] = "Forte Compra"
        elif score_total >= 0.5:
            resultado['decisao'] = "Compra"
        elif score_total <= -2.0:
            resultado['decisao'] = "Forte Venda"
        elif score_total <= -0.5:
            resultado['decisao'] = "Venda"
        else:
            resultado['decisao'] = "Neutro"
        
        # Adicionar informações de risco
        atr = df['atr_14'].iloc[-1]
        preco = df['Close'].iloc[-1]
        
        resultado['gestao_risco'] = {
            "atr_14": atr,
            "atr_percentual": (atr / preco) * 100,
            "stop_sugerido": preco - (2.5 * atr),
            "volatilidade": "Alta" if (atr/preco) > 0.03 else "Normal"
        }
        
        return resultado
    
    def executar_screener(self, lista_tickers):
        """Executa screener completo para lista de tickers"""
        resultados = []
        
        for ticker in lista_tickers:
            try:
                resultado = self.calcular_score_final(ticker)
                if resultado:
                    resultados.append(resultado)
                    print(f"✓ {ticker}: {resultado['decisao']} (Score: {resultado['score_total']:.2f})")
            except Exception as e:
                print(f"✗ Erro processando {ticker}: {e}")
        
        # Ordenar por score
        resultados.sort(key=lambda x: x['score_total'], reverse=True)
        
        return resultados

# Exemplo de uso
if __name__ == "__main__":
    # Lista de exemplo - substitua por seus tickers de interesse
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN']
    
    screener = ScreenerAvancado()
    resultados = screener.executar_screener(tickers)
    
    print("\n" + "="*60)
    print("RESULTADOS DO SCREENER")
    print("="*60)
    
    for resultado in resultados[:10]:  # Top 10
        print(f"\n{resultado['ticker']} - {resultado['decisao']}")
        print(f"Score: {resultado['score_total']:.2f}")
        print(f"Preço: ${resultado['preco']:.2f}")
        
        # Mostrar top 3 critérios que mais contribuíram
        criterios_ordenados = sorted(
            resultado['criterios'].items(),
            key=lambda x: abs(x[1]['sinal'] * x[1]['peso']),
            reverse=True
        )
        
        print("Top critérios:")
        for nome, dados in criterios_ordenados[:3]:
            sinal_texto = "Compra" if dados['sinal'] > 0 else "Venda" if dados['sinal'] < 0 else "Neutro"
            forca = dados['detalhes'].get('forca', 'N/A')
            print(f"  • {nome}: {sinal_texto} ({forca})")
