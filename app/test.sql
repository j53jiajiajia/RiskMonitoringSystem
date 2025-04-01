INSERT INTO positions (client_id, symbol, quantity, cost_basis)
VALUES
  (1, 'AAPL', 100, 150.00),
  (1, 'TSLA', 50, 700.00),
  (2, 'GOOGL', 80, 120.00),
  (2, 'MSFT', 120, 210.00);


INSERT INTO margin (client_id, loan)
VALUES
  (1, 10000.00),
  (2, 150000.00);

