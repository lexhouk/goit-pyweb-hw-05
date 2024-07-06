console.log('Hello world!')

const ws = new WebSocket('ws://localhost:8080')

formChat.addEventListener('submit', (e) => {
    e.preventDefault()
    ws.send(textField.value)
    textField.value = null
})

ws.onopen = (e) => {
    console.log('Hello WebSocket!')
}

ws.onmessage = (e) => {
    console.log(e.data)
    text = e.data

    const elMsg = document.createElement('div')

    elMsg.innerHTML = text
        .replace(/\n/g, '\n\t')
        .replace(/\n/g, '<br>')
        .replace(/\t/g, '\t'.repeat(2))
        .replace(/\t/g, '&nbsp;'.repeat(3))

    subscribe.appendChild(elMsg)
}
