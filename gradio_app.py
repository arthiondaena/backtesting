import gradio as gr
from data_fetcher import fetch
from indicators import SMC
from strategies import smc_plot_backtest, smc_ema_plot_backtest
import pandas as pd

symbols = pd.read_csv('data/Ticker_List_NSE_India.csv')

def run(stock, strategy, swing_hl, ema1, ema2, cross_close):
    ticker =  symbols[symbols['NAME OF COMPANY'] == stock]['YahooEquiv'].values[0]
    data = fetch(ticker, period='1mo', interval='15m')

    smc_plot_backtest(data, 'test.html', swing_hl)

    signal_plot = SMC(data=data, swing_hl_window_sz=swing_hl).plot(show=False).update_layout(title=dict(text=ticker))
    backtest_plot = gr.Plot()

    if strategy == "SMC":
        backtest_plot = smc_plot_backtest(data, 'test.html', swing_hl)

    if strategy == "SMC with EMA":
        backtest_plot = smc_ema_plot_backtest(data, 'test.html', ema1, ema2, cross_close)

    return signal_plot, backtest_plot


with gr.Blocks(fill_width=True) as app:
    gr.Markdown(
        '# Algorithmic Trading Dashboard'
    )
    stock = gr.Dropdown(symbols['NAME OF COMPANY'].unique().tolist(), label='Select Company', value=None)

    with gr.Row():
        strategy = gr.Dropdown(['SMC', 'SMC with EMA'], label='Strategy', value=None)
        swing_hl = gr.Number(label="Swing High/Low Window Size", value=10, interactive=True)

    @gr.render(inputs=[strategy])
    def show_extra(strat):
        if strat == "SMC with EMA":
            with gr.Row():
                ema1 = gr.Number(label='Fast EMA length', value=9)
                ema2 = gr.Number(label='Slow EMA length', value=21)
                cross_close = gr.Checkbox(label='Close trade on EMA crossover')
            input = [stock, strategy, swing_hl, ema1, ema2, cross_close]

        elif strat == "SMC":
            input = [stock, strategy, swing_hl]
        else:
            input = []

        btn.click(
            run,
            inputs=input,
            outputs=[signal_plot, backtest_plot]
        )

    btn = gr.Button("Run")

    with gr.Row():
        signal_plot = gr.Plot(label='Signal plot')

    with gr.Row():
        backtest_plot = gr.Plot(label='Backtesting plot')

app.launch(debug=True)