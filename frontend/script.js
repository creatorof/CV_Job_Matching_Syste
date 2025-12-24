function createItem() {
  fetch("http://localhost:8000/items?name=hello", {
    method: "POST"
  })
    .then(res => res.json())
    .then(data => console.log(data))
    .catch(err => console.error(err));
}
