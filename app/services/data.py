import pandas as pd

# vnstock only
try:
	import vnstock as _vnstock
	print("[data] vnstock imported OK (vnstock3 disabled)")
except Exception as e:
	_vnstock = None
	print(f"[data] vnstock import FAILED: {e}")

# Optional helpers if exposed
try:
	from vnstock import Vnstock as _VnstockClient
except Exception:
	_VnstockClient = None

try:
	from vnstock import stock_historical_data as _stock_hist_fn
except Exception:
	_stock_hist_fn = None

try:
	from vnstock.stock import stock_historical_data as _stock_hist_fn_mod
except Exception:
	_stock_hist_fn_mod = None


def _normalize_price_df(df: pd.DataFrame) -> pd.DataFrame:
	if df is None or df.empty:
		print("[data] normalize: empty input")
		return pd.DataFrame()
	df = df.copy()
	df.columns = [str(c).strip() for c in df.columns]
	df = df.rename(columns={c: str(c).lower() for c in df.columns})
	# Date
	if 'time' in df.columns and 'date' not in df.columns:
		df = df.rename(columns={'time': 'date'})
	elif 'tradingdate' in df.columns and 'date' not in df.columns:
		df = df.rename(columns={'tradingdate': 'date'})
	elif 'date' not in df.columns and 'ngay' in df.columns:
		df = df.rename(columns={'ngay': 'date'})
	# OHLCV
	aliases = {
		'open': ['open', 'o', 'openprice', 'gia_mo_cua'],
		'high': ['high', 'h', 'gia_cao_nhat'],
		'low': ['low', 'l', 'gia_thap_nhat'],
		'close': ['close', 'c', 'closeprice', 'adjustclose', 'adj close', 'gia_dong_cua'],
		'volume': ['volume', 'v', 'totalvol', 'khoi_luong']
	}
	for std, cands in aliases.items():
		if std not in df.columns:
			for c in cands:
				if c in df.columns:
					df = df.rename(columns={c: std})
					break
	if 'date' not in df.columns:
		print(f"[data] normalize: missing date; cols={list(df.columns)}")
		return pd.DataFrame()
	try:
		df['date'] = pd.to_datetime(df['date']).dt.date
	except Exception as e:
		print(f"[data] normalize: date parse error: {e}")
		return pd.DataFrame()
	# Coerce numeric columns to numbers (remove thousand separators)
	for col in ['open', 'high', 'low', 'close', 'volume']:
		if col in df.columns:
			ser = df[col].astype(str).str.replace(',', '', regex=False).str.replace(' ', '', regex=False).str.replace('\u00a0', '', regex=False)
			df[col] = pd.to_numeric(ser, errors='coerce')
	keep = [c for c in ['date', 'open', 'high', 'low', 'close', 'volume'] if c in df.columns]
	if not keep:
		print(f"[data] normalize: no OHLCV; cols={list(df.columns)}")
		return pd.DataFrame()
	df = df[keep].drop_duplicates(subset=['date']).sort_values('date')
	print(f"[data] normalize: shape={df.shape}, dtypes={{k:str(v) for k,v in df.dtypes.items()}}")
	return df


def _try_vnstock_function(symbol: str, start: str, end: str) -> pd.DataFrame:
	print(f"[data] vnstock function path: {symbol} {start}->{end}")
	# Try direct function imports
	for fn_name, fn in [("direct", _stock_hist_fn), ("module", _stock_hist_fn_mod)]:
		if fn is None:
			continue
		# Try positional then keyword styles
		for call_style in [
			{"args": (symbol, start, end), "kwargs": {"resolution": "1D", "type": "stock"}},
			{"args": (), "kwargs": {"symbol": symbol, "start": start, "end": end, "resolution": "1D", "type": "stock"}},
		]:
			try:
				df = fn(*call_style["args"], **call_style["kwargs"])
				print(f"[data] vnstock function [{fn_name}/{'pos' if call_style['args'] else 'kw'}] returned: {None if df is None else df.shape}")
				ndf = _normalize_price_df(df)
				if not ndf.empty:
					return ndf
			except TypeError as e:
				print(f"[data] vnstock function [{fn_name}] TypeError: {e}")
			except Exception as e:
				print(f"[data] vnstock function [{fn_name}] error: {e}")
	# Try attribute on package if exposed
	try:
		fn_attr = getattr(_vnstock, 'stock_historical_data', None)
		if fn_attr is not None:
			df = fn_attr(symbol, start, end, resolution='1D', type='stock')
			print(f"[data] vnstock function [attr] returned: {None if df is None else df.shape}")
			return _normalize_price_df(df)
	except Exception as e:
		print(f"[data] vnstock function [attr] error: {e}")
	return pd.DataFrame()


def _try_vnstock_class(symbol: str, start: str, end: str) -> pd.DataFrame:
	print(f"[data] vnstock class path: {symbol} {start}->{end}")
	if _VnstockClient is None:
		print("[data] Vnstock client class not available")
		return pd.DataFrame()
	upper_symbol = (symbol or "").strip().upper()
	for source in ['VCI', 'TCBS', 'SSI']:
		try:
			client = _VnstockClient()
			stock_obj = client.stock(upper_symbol, source=source)
			# First variant: period
			try:
				df = stock_obj.quote.history(period='1D', start=start, end=end)
				print(f"[data] vnstock class [{source} period] returned: {None if df is None else df.shape}")
				ndf = _normalize_price_df(df)
				if not ndf.empty:
					return ndf
			except Exception as e1:
				print(f"[data] vnstock class [{source} period] error: {e1}")
			# Second variant: interval
			try:
				df = stock_obj.quote.history(start=start, end=end, interval='1D')
				print(f"[data] vnstock class [{source} interval] returned: {None if df is None else df.shape}")
				ndf = _normalize_price_df(df)
				if not ndf.empty:
					return ndf
			except Exception as e2:
				print(f"[data] vnstock class [{source} interval] error: {e2}")
		except Exception as outer:
			print(f"[data] vnstock class [{source}] outer error: {outer}")
	return pd.DataFrame()


def fetch_price_history(symbol: str, start: str, end: str) -> pd.DataFrame:
	print(f"[data] fetch_price_history: symbol={symbol}, start={start}, end={end}")
	df = _try_vnstock_function(symbol, start, end)
	if not df.empty:
		print("[data] source used: vnstock.function")
		return df
	df = _try_vnstock_class(symbol, start, end)
	if not df.empty:
		print("[data] source used: vnstock.class")
		return df
	print("[data] no data from vnstock")
	try:
		print(f"[data] dir(vnstock) sample: {sorted([n for n in dir(_vnstock) if 'stock' in n.lower()])[:10]}")
	except Exception:
		pass
	return pd.DataFrame()


def validate_dates(start: str, end: str):
	s = pd.to_datetime(start).date()
	e = pd.to_datetime(end).date()
	if s > e:
		s, e = e, s
	return s.isoformat(), e.isoformat()
