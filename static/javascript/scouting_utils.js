function increment(id) {
    const input = document.getElementById(id);
    input.value = parseInt(input.value) + 1;
}

function decrement(id) {
    const input = document.getElementById(id);
    const value = parseInt(input.value);
    if (value > 0) {
        input.value = value - 1;
    }
}