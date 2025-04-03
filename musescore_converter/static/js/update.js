function handleClickDownload(score_id){
    body = JSON.stringify({"score_id": score_id})
    console.log(body)
    fetch("/api/download", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: body
    })
}


function create_score_div(score){
    div_score = document.createElement("div")
    div_score.id = score.id
    div_score.classList.add("score")
    
    div_infos = document.createElement("div")
    div_title = document.createElement("h2")
    div_title.textContent = score.title
    div_author = document.createElement("div")
    div_author.textContent = score.author
    div_composer = document.createElement("div")
    div_composer.textContent = score.composer
    div_pages = document.createElement("div")
    div_pages.textContent = `Number of pages saved: ${score.num_pages}`
    
    div_infos.appendChild(div_title)
    div_infos.appendChild(div_author)
    div_infos.appendChild(div_composer)
    div_infos.appendChild(div_pages)
    

    buttonEl = document.createElement("button")
    buttonEl.addEventListener('click', function() {
        handleClickDownload(score.id);
    });
    buttonEl.textContent = "Download"
    div_score.appendChild(div_infos)
    div_score.appendChild(buttonEl)
    return div_score
}

function updateScoresList(score_list){
    container = document.querySelector(".scores-container")
    children = []
    score_list.forEach(score => {
        score_div = create_score_div(score)
        children.push(score_div)
    });
    
    container.replaceChildren(...children)
}

function updateStatus(status){
    const statusCircle = document.getElementById("status-circle");
    const statusMessage = document.getElementById("status-message");

    if (status.is_active === true) {
        statusMessage.textContent = "Active";
        statusCircle.style.background = "#4CAF50"; 
    } else {
        statusMessage.textContent = "Inactive";
        statusCircle.style.background = "#bbb"; 
    }
}



const scoresMap = new Set();
const socket = new WebSocket("ws://" + window.location.host + "/ws");
socket.onmessage = function (event) {
    try {
        const message = JSON.parse(event.data);
        if(message.scores){
            updateScoresList(message.scores)
        }
        if(message.status){
            updateStatus(message.status)
        }
        // if (!scoresMap.has(score_id)){
        //     addScoreElement(score_id, data.pages)
        //     scoresMap.add(score_id)
        // } else {
        //     updateScoreElement(score_id, data.pages)
        // }
        
        
        // const messagesList = document.getElementById("messages-list");
        // const listItem = document.createElement("li");
        // listItem.textContent = data.message;  // Display the message

        // // Change color based on status
        // if (data.status === "success") {
        //     listItem.style.color = "green";
        // } else if (data.status === "error") {
        //     listItem.style.color = "red";
        // } else if (data.status === "warning") {
        //     listItem.style.color = "orange";
        // } else {
        //     listItem.style.color = "black";  // Default color
        // }

        // messagesList.prepend(listItem);  // Add the new message at the top
    } catch (error) {
        console.error("Error parsing WebSocket message:", error);
    }
};