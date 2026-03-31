const API_URL = "http://127.0.0.1:8000";

async function fetchStats() {
    const res = await fetch(`${API_URL}/dashboard`);
    const data = await res.json();
    document.getElementById('burn-val').innerText = data.monthly_exp || "₹0";
    document.getElementById('trial-val').innerText = data.active_trials || 0;
}

async function addBill() {
    const payload = {
        name: document.getElementById('name').value,
        price: parseFloat(document.getElementById('price').value),
        category: document.getElementById('category').value,
        date: document.getElementById('date').value,
        is_trial: false
    };

    try {
        const res = await fetch("http://127.0.0.1:8000/add-bill", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const result = await res.json();
        
        if (res.ok) {
            alert("Success! " + result.message);
            updateDash(); // Refresh the numbers
        } else {
            console.error("Server Error:", result);
            alert("Error: " + (result.detail || "Check console"));
        }
    } catch (err) {
        console.error("Connection Refused:", err);
        alert("Is the Uvicorn server running?");
    }
}

// Initial load
fetchStats();