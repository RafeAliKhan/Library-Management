guard(); renderNav();
const $ = (id) => document.getElementById(id);
let timer;

async function loadGenres() {
  (await api("/books/genres")).forEach((g) => $("genre").insertAdjacentHTML("beforeend", `<option>${esc(g)}</option>`));
}

async function loadBooks() {
  const params = new URLSearchParams({ q: $("search").value, genre: $("genre").value });
  const books = await api("/books?" + params);
  $("books").innerHTML = books.map((b) => `
    <tr><td>${esc(b.title)}</td><td>${esc(b.author)}</td><td>${esc(b.genre)}</td><td>${b.stock}</td>
    <td><button ${b.stock < 1 ? "disabled" : ""} onclick="borrow(${b.id})">Borrow</button></td></tr>`).join("")
    || '<tr><td colspan="5">No books found</td></tr>';
}

async function borrow(id) {
  try {
    const r = await api("/loans", "POST", { book_id: id });
    $("msg").className = "ok"; $("msg").textContent = "Borrowed! Due " + r.due_date;
    loadBooks();
  } catch (e) { $("msg").className = "error"; $("msg").textContent = e.message; }
}

$("search").oninput = () => { clearTimeout(timer); timer = setTimeout(loadBooks, 250); };  // live search, no reload
$("genre").onchange = loadBooks;
loadGenres(); loadBooks();
