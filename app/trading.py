import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import datetime
from .models import User, Portfolio
from . import db

def preprocess_data(stock_symbol, period="5y"):
    # Download stock data
    data = yf.download(stock_symbol, period=period, interval='1d')
    
    # Replace zero prices with a small epsilon value and convert to logarithmic scale
    data['Adj Close'] = data['Adj Close'].replace(0, np.finfo(float).eps)
    data['Log Close'] = np.log(data['Adj Close'])
    
    return data

def create_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dense(25))
    model.add(Dense(1))  # Regression output for next day's price

    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train_model(stock_symbol):
    # Preprocess data
    data = preprocess_data(stock_symbol)

    # Use only the 'Log Close' column for training
    prices = data['Log Close'].values
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_prices = scaler.fit_transform(prices.reshape(-1, 1))

    # Prepare training data
    X_train, y_train = [], []
    for i in range(30, len(scaled_prices)):
        X_train.append(scaled_prices[i-30:i, 0])
        y_train.append(scaled_prices[i, 0])
    
    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    
    # Create and train the model
    model = create_lstm_model((X_train.shape[1], 1))
    model.fit(X_train, y_train, batch_size=1, epochs=1)  # Use more epochs for better results

    return model, scaler

def predict_next_day(model, scaler, recent_data):
    # Prepare input data (last 30 days)
    recent_data_scaled = scaler.transform(recent_data.reshape(-1, 1))
    X_test = np.array([recent_data_scaled])
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    
    # Predict the next day's price
    predicted_price = model.predict(X_test)
    predicted_price = scaler.inverse_transform(predicted_price)
    return predicted_price[0, 0]

def auto_trade(stock_symbol, user_id, stop_loss_fraction):
    user = User.query.get(user_id)
    portfolio = Portfolio.query.filter_by(user_id=user_id, stock_symbol=stock_symbol).first()

    if not portfolio:
        portfolio = Portfolio(user_id=user_id, stock_symbol=stock_symbol, quantity=0, initial_value=0)
        db.session.add(portfolio)
        db.session.commit()

    model, scaler = train_model(stock_symbol)
    data = preprocess_data(stock_symbol)
    
    cash = portfolio.initial_value  # Start with the initial value
    stop_loss_value = cash * stop_loss_fraction
    
    for i in range(30, len(data)):
        recent_data = data['Log Close'].values[i-30:i]
        predicted_price = predict_next_day(model, scaler, recent_data)
        current_price = np.exp(data['Log Close'].values[i])

        # If price is predicted to rise, buy or hold
        if predicted_price > current_price:
            if portfolio.quantity == 0:
                quantity_to_buy = cash // current_price
                cash -= quantity_to_buy * current_price
                portfolio.quantity += quantity_to_buy
            # Else, hold
        # If price is predicted to fall, sell if owned
        else:
            if portfolio.quantity > 0:
                cash += portfolio.quantity * current_price
                portfolio.quantity = 0
        
        # Check stop loss condition
        total_value = cash + (portfolio.quantity * current_price)
        if total_value < stop_loss_value:
            cash += portfolio.quantity * current_price
            portfolio.quantity = 0
            break
    
    # Update portfolio
    portfolio.initial_value = cash
    db.session.commit()
