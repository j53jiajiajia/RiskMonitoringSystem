import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend
} from "recharts";

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#AA66CC', '#FF4444'];

function App() {
  const [clientId, setClientId] = useState(null);
  const [clientList, setClientList] = useState([]);
  const [positions, setPositions] = useState([]);
  const [marginStatus, setMarginStatus] = useState(null);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({ symbol: '', quantity: '', cost_basis: '' });

  useEffect(() => {
    fetchClientList();
  }, []);

  useEffect(() => {
    if (clientId !== null) {
      fetchData();
      const interval = setInterval(fetchData, 10000);
      return () => clearInterval(interval);
    }
  }, [clientId]);

  const fetchClientList = async () => {
    try {
      const res = await axios.get("http://localhost:5000/api/clients");
      setClientList(res.data);
      if (res.data.length > 0) {
        setClientId(res.data[0]);
      }
    } catch (err) {
      console.error("Failed to fetch client list:", err);
      setError("Failed to load client list.");
    }
  };

  const fetchData = async () => {
    try {
      const posRes = await axios.get(`http://localhost:5000/api/positions/${clientId}`);
      const marginRes = await axios.get(`http://localhost:5000/api/margin-status/${clientId}`);
      setPositions(posRes.data);
      setMarginStatus(marginRes.data);
      setError(null);
    } catch (err) {
      console.error("Error fetching data:", err);
      setError("Failed to connect to backend.");
    }
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://localhost:5000/api/positions", {
        client_id: clientId,
        symbol: form.symbol,
        quantity: parseInt(form.quantity),
        cost_basis: parseFloat(form.cost_basis)
      });
      setForm({ symbol: '', quantity: '', cost_basis: '' });
      fetchData();
    } catch (err) {
      console.error("Error adding position:", err);
      alert("Failed to add position");
    }
  };

  const chartData = Object.values(
    positions.reduce((acc, p) => {
      const symbol = p.symbol;
      const value = Number(p.quantity) * Number(p.current_price || 0);
      if (!acc[symbol]) {
        acc[symbol] = { symbol, value };
      } else {
        acc[symbol].value += value;
      }
      return acc;
    }, {})
  );


  return (
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif", maxWidth: "900px", margin: "auto" }}>
      <h1>📊 Risk Monitoring Dashboard</h1>

      <div style={{ marginBottom: "1rem" }}>
        <label>
          Select Client:{" "}
          <select
            value={clientId ?? ""}
            onChange={(e) => setClientId(Number(e.target.value))}
            disabled={clientList.length === 0}
            style={{ padding: "0.3rem" }}
          >
            {clientList.map((id) => (
              <option key={id} value={id}>
                Client {id}
              </option>
            ))}
          </select>
        </label>
      </div>

      <form onSubmit={handleFormSubmit} style={{ marginBottom: "2rem", display: "flex", gap: "1rem", flexWrap: "wrap" }}>
        <input type="text" name="symbol" placeholder="Symbol" value={form.symbol} onChange={handleFormChange} required />
        <input type="number" name="quantity" placeholder="Quantity" value={form.quantity} onChange={handleFormChange} required />
        <input type="number" step="0.01" name="cost_basis" placeholder="Cost Basis" value={form.cost_basis} onChange={handleFormChange} required />
        <button type="submit">Add Position</button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <h2>📦 Positions</h2>
      <table border="1" cellPadding="8" style={{ marginBottom: "2rem", width: "100%" }}>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Quantity</th>
            <th>Cost Basis</th>
            <th>Current Price</th>
          </tr>
        </thead>
        <tbody>
            {positions.map((pos, index) => (
              <tr key={`${pos.symbol}-${index}`}>
              <td>{pos.symbol}</td>
              <td>{pos.quantity}</td>
              <td>${Number(pos.cost_basis).toFixed(2)}</td>
              <td>
                {typeof pos.current_price === "number"
                  ? `$${Number(pos.current_price).toFixed(2)}`
                  : "N/A"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>📉 Margin Status</h2>
      {marginStatus ? (
        <div
          style={{
            border: "2px solid",
            borderColor: marginStatus.margin_call ? "red" : "green",
            padding: "1rem",
            borderRadius: "8px",
            background: marginStatus.margin_call ? "#ffe5e5" : "#e7ffe7"
          }}
        >
          <p>💰 Portfolio Value: ${Number(marginStatus.portfolio_value).toFixed(2)}</p>
          <p>🏦 Loan: ${Number(marginStatus.loan).toFixed(2)}</p>
          <p>📈 Net Equity: ${Number(marginStatus.net_equity).toFixed(2)}</p>
          <p>📊 Margin Requirement: ${Number(marginStatus.margin_requirement).toFixed(2)}</p>
          <p>🚨 Margin Shortfall: ${Number(marginStatus.margin_shortfall).toFixed(2)}</p>
          <p>
            {marginStatus.margin_call ? (
              <span style={{ color: "red", fontWeight: "bold" }}>⚠️ Margin Call Triggered!</span>
            ) : (
              <span style={{ color: "green" }}>✅ No Margin Call</span>
            )}
          </p>
        </div>
      ) : (
        <p>Loading margin status...</p>
      )}

      <h2 style={{ marginTop: "2rem" }}>📊 Position Value Distribution</h2>
      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="symbol"
              cx="50%"
              cy="50%"
              outerRadius={100}
              label
            >
              {chartData.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <p>No data to visualize.</p>
      )}
    </div>
  );
}

export default App;
