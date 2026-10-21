guard(); renderNav();
const $ = (id) => document.getElementById(id);

async function load() {
  const { loans, fine_balance } = await api("/me/loans");
  $("fines").textContent = "$" + fine_balance.toFixed(2);
  $("loans").innerHTML = loans.map((l) => `
    <tr><td>${esc(l.title)}</td><td>${l.due_date}</td>
    <td class="${l.overdue ? "overdue" : ""}">${l.returned_at ? "Returned " + l.returned_at : l.overdue ? "OVERDUE" : "On loan"}</td>
    <td>$${l.fine.toFixed(2)}</td>
    <td>${l.returned_at ? "" : `<button onclick="ret(${l.id})">Return</button>`}</td></tr>`).join("")
    || '<tr><td colspan="5">No loans yet</td></tr>';
}

async function ret(id) {
  try { await api(`/loans/${id}/return`, "POST"); load(); }
  catch (e) { $("msg").className = "error"; $("msg").textContent = e.message; }
}
load();
