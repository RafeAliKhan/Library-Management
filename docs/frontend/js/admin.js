guard(true); renderNav();
const $ = (id) => document.getElementById(id);
const say = (t, cls) => { $("msg").className = cls; $("msg").textContent = t; };

async function loadBooks() {
  const books = await api("/books");
  $("books").innerHTML = books.map((b) => `
    <tr><td>${esc(b.title)}</td><td>${esc(b.author)}</td>
    <td><input type="number" min="0" value="${b.stock}" style="width:70px" onchange="updateStock(${b.id}, this.value)"></td>
    <td><button class="danger" onclick="del(${b.id})">Delete</button></td></tr>`).join("");
}

async function loadOverdue() {
  const rows = await api("/admin/overdue");
  $("overdue").innerHTML = rows.map((r) => `
    <tr><td>${esc(r.name)}</td><td>${esc(r.email)}</td><td>${esc(r.title)}</td>
    <td class="overdue">${r.due_date}</td><td>$${r.fine.toFixed(2)}</td></tr>`).join("")
    || '<tr><td colspan="5">Nothing overdue 🎉</td></tr>';
}

async function updateStock(id, v) {
  try { await api("/books/" + id, "PUT", { stock: v }); say("Stock updated", "ok"); }
  catch (e) { say(e.message, "error"); loadBooks(); }
}

async function del(id) {
  if (!confirm("Delete this book?")) return;
  await api("/books/" + id, "DELETE"); loadBooks();
}

$("add").onclick = async () => {
  try {
    await api("/books", "POST", {
      title: $("title").value, author: $("author").value, genre: $("genre").value,
      isbn: $("isbn").value, stock: $("stock").value,
    });
    say("Book added", "ok");
    ["title", "author", "genre", "isbn"].forEach((f) => ($(f).value = ""));
    loadBooks();
  } catch (e) { say(e.message, "error"); }
};
loadBooks(); loadOverdue();
