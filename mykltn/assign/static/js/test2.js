const all_group_chairman = document.querySelectorAll('.group-chairman');
const all_group_vice = document.querySelectorAll('.group-vice');
const all_group_secretary = document.querySelectorAll('.group-secretary');
const all_group_normal = document.querySelectorAll('.group-normal');
const all_group_member = document.querySelectorAll('.group-member');
let drag_lecturer = null;

all_group_member.forEach((group_member) => {
    group_member.addEventListener("dragstart", dragStart);
    group_member.addEventListener("dragend", dragEnd);
});

function dragStart(){
    drag_lecturer = this;
    drag_lecturer.style.backgroundColor = "lightgray";
    console.log("DragStart");
};
function dragEnd(){
    drag_lecturer.style.backgroundColor = "white";
    drag_lecturer = null;
    console.log("DragEnd");
};


all_group_chairman.forEach((group_chairman)=> {
    group_chairman.addEventListener("dragover", dragOver);
    group_chairman.addEventListener("drop", chairmanDrop);
});

function chairmanDrop(e){
    var committee_id = $(this).data('id');
    var degree_workplace_id = $(drag_lecturer).data('id');
    var my_arr = degree_workplace_id.split('-');
    var degree_id = my_arr[0];
    var work_place_id = my_arr[1];
    var lecturer_id = my_arr[2];

    if (degree_id <= 2 &&  work_place_id == 1) {
        drag_lecturer.classList.add('group-member');
        this.appendChild(drag_lecturer);

        $("#change-submit").append("<input type='hidden' name='change' value='1-"+ committee_id +"-" + lecturer_id +"'>");
    } else {
        alert("Giảng viên không đủ điều kiện để trở thành Chủ tịch của hội đồng");
    };

    


};

all_group_vice.forEach((group_vice)=> {
    group_vice.addEventListener("dragover", dragOver);
    group_vice.addEventListener("drop", viceDrop);
});

function viceDrop(e){
    var committee_id = $(this).data('id');
    var degree_workplace_id = $(drag_lecturer).data('id');
    var my_arr = degree_workplace_id.split('-');
    var degree_id = my_arr[0];
    var work_place_id = my_arr[1];
    var lecturer_id = my_arr[2];

    if (degree_id <= 2) {
        drag_lecturer.classList.add('group-member');
        this.appendChild(drag_lecturer);

        $("#change-submit").append("<input type='hidden' name='change' value='2-"+ committee_id +"-" + lecturer_id +"'>");
    } else {
        alert("Giảng viên không đủ điều kiện để trở thành Phó chủ tịch của hội đồng");
    };

    

};

all_group_secretary.forEach((group_secretary)=> {
    group_secretary.addEventListener("dragover", dragOver);
    group_secretary.addEventListener("drop", secretaryDrop);
});

function secretaryDrop(e){
    var committee_id = $(this).data('id');
    var degree_workplace_id = $(drag_lecturer).data('id');
    var my_arr = degree_workplace_id.split('-');
    var degree_id = my_arr[0];
    var work_place_id = my_arr[1];
    var lecturer_id = my_arr[2];

    if ( work_place_id == 1) {
        drag_lecturer.classList.add('group-member');
        this.appendChild(drag_lecturer);

        $("#change-submit").append("<input type='hidden' name='change' value='3-"+ committee_id +"-" + lecturer_id +"'>");
    } else {
        alert("Giảng viên không đủ điều kiện để trở thành Thư ký của Hội đồng");
    };

    

};

all_group_normal.forEach((group_normal)=> {
    group_normal.addEventListener("dragover", dragOver);
    group_normal.addEventListener("drop", normalDrop);
});

function normalDrop(e){
    var committee_id = $(this).data('id');
    var degree_workplace_id = $(drag_lecturer).data('id');
    var my_arr = degree_workplace_id.split('-');
    var degree_id = my_arr[0];
    var work_place_id = my_arr[1];
    var lecturer_id = my_arr[2];

    drag_lecturer.classList.add('group-chairman');
    this.appendChild(drag_lecturer);

    $("#change-submit").append("<input type='hidden' name='change' value='4-"+ committee_id +"-" + lecturer_id +"'>");
    
};

function dragOver(e){
    e.preventDefault();
    console.log("DragOver");
};
