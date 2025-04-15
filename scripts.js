let users = JSON.parse(localStorage.getItem('users')) || [];

function showLoginForm() { toggleForms('loginForm'); }
function showRegisterForm() { toggleForms('registerForm'); }
function showDashboard() { toggleForms('dashboard'); }

function toggleForms(show) {
  document.querySelectorAll('.auth-form, #dashboard').forEach(el => el.classList.add('hidden'));
  document.getElementById(show).classList.remove('hidden');
}

function login() {
  alert('Login successful!');
  showDashboard();
}

function register() {
  alert('Registration successful!');
  showLoginForm();
}

function simulateData() {
  return {
    ph: 7 + Math.random() * 0.5,
    turbidity: 20 + Math.random() * 5,
    temp: 25 + Math.random() * 2,
    level: 50 + Math.random() * 10
  };
}

let charts = {};
window.onload = function() {
  showLoginForm();
  ['ph', 'turbidity', 'temp', 'level'].forEach(id => {
    let ctx = document.getElementById(id + 'Chart').getContext('2d');
    charts[id] = new Chart(ctx, {
      type: 'line',
      data: { labels: [], datasets: [{ label: id.toUpperCase(), borderColor: '#007bff', data: [], fill: false }] }
    });
  });
  setInterval(updateData, 2000);
};

function updateData() {
  let data = simulateData();
  ['ph', 'turbidity', 'temp', 'level'].forEach(id => {
    document.getElementById(id).innerText = data[id].toFixed(2);
    let chart = charts[id];
    chart.data.labels.push(new Date().toLocaleTimeString());
    chart.data.datasets[0].data.push(data[id]);
    if (chart.data.labels.length > 10) {
      chart.data.labels.shift();
      chart.data.datasets[0].data.shift();
    }
    chart.update();
  });
}
