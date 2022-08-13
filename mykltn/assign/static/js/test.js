const all_topic = document.querySelectorAll('.card-name-topic');
const all_group = document.querySelectorAll('.card-group-topic');
let drag_topic = null;

all_topic.forEach((card_name_topic) => {
    card_name_topic.addEventListener("dragstart", dragStart);
    card_name_topic.addEventListener("dragend", dragEnd);
});

function dragStart(){
    drag_topic = this;
    drag_topic.style.backgroundColor = "lightgray";
    console.log("DragStart");
};
function dragEnd(){
    drag_topic.style.backgroundColor = "white";
    drag_topic = null;
    console.log("DragEnd");
};



all_group.forEach((card_group_topic) => {
    card_group_topic.addEventListener("dragover", dragOver);
    card_group_topic.addEventListener("dragenter", dragEnter);
    card_group_topic.addEventListener("dragleave", dragLeave);
    card_group_topic.addEventListener("drop", dragDrop);
});

function dragOver(e){
    e.preventDefault()
    console.log("DragOver");
};

function dragEnter(){
    console.log("DragEnter");
};

function dragLeave(){
    console.log("DragLeave");
};

function dragDrop(e){
    drag_topic.classList.add("card-name-topic");
    this.appendChild(drag_topic);
    console.log(drag_topic.classList);

    var group_id = $(this).data('id');
    console.log(group_id);
    var topic_id = $(drag_topic).data('id');
    console.log(topic_id);

    $("#change-submit").append("<input type='hidden' name='change' value='"+ topic_id +"-" + group_id +"'>");

};  