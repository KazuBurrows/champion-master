$(document).ready(function() {
    console.log("Doc ready test");
    

    get_all_champions();


    $('#roll_model').hide();
    
    $("#roll_model").click(function(){
        $('#roll_model').hide();
        $("#roll_model").css("display", "none");

    
    });
    

    $("#add_close").click(function(){
        $('#add_model').hide();
        $("#add_model").css("display", "none");
    });

    $("#update_close").click(function(){
        $('#update_model').hide();
        $("#update_model").css("display", "none");
    });

    $("#tag_close").click(function(){
        // console.log("close")
        $('#tag_model').hide();
        $("#tag_model").css("display", "none");

        //Removes contents in tag modal
        var list = document.getElementById("tag_champion");
        while (list.hasChildNodes()) {  
            list.removeChild(list.firstChild);

        }
    });


    $('#search_name').on('change keyup paste', function() {

        search_name = $("#search_name").val();
        db_type = "0"

        query = db_type+search_name

        if (search_name.length > 0) {
            refine_pool(query);

        } else {

            // refine_champion_pool should be sent but can't be bothered to 
            // repopulate the array to be the same as all_champions
            populate_div(all_champions);


        }

    });
    
    //when enter key is pressed when input field is focused
    $('#search_tag').keypress(function(event){
        if(event.keyCode == 13){
          $('#submit_tag_btn').click();
        }
      });

    $('#search_tag').on('change keyup paste', function() {

        search_name = $("#search_tag").val();


        if (search_name.length == 0) {

            // refine_champion_pool should be sent but can't be bothered to 
            // repopulate the array to be the same as all_champions
            populate_div(all_champions);


        }

    });
    
    $('#submit_tag_btn').click(function(){
        var tag_name = $("#search_tag").val();
        var db_type = "1";

        var query = db_type + tag_name;
        refine_pool(query);

        // console.log("submit tag_name: " + tag_name);
    });

});




function add_button() {
    // $('#add_champion').toggle();

    $('#add_model').show();
    $("#add_model").css("display", "block");

}

function update_button(id) {
    console.log("Update button: " + id);
    // $('#update_champion').toggle();
    $('#update_model').show();
    $("#update_model").css("display", "block");


    // $(".tag_identifier").remove();
    update_modal_fill(id);

}


function remove_tag(id, tag_name) {
    console.log("remove tag function " + id, tag_name);

    var query = new Array(2);
    query[0] = id;
    query[1] = tag_name;


    //now contact app.py to delete tag
    $.ajax({
        type : "POST",
        url : '/delete_tag_route/' + query + ''
        }).done(function() {
            

            
        });

}


var all_champions = new Array(300);
//this array gets reset then champions inserted, for now
var refine_champion_pool = new Array(300);
var selected_array = new Array(300);
// var refined_array = new Array(300);

class Champion {
    constructor(id, name, icon) {
        this.champId = id;
        this.champName = name;
        this.champIcon = icon;

    }
}

// append all champions in 'all_champions' array
function get_all_champions() {
    $.ajax({
        type : "GET",
        url : '/get_all_champions/'
        }).done(function(json_all_champions) {
            //turn json to js object
            json_all_champions = JSON.parse(json_all_champions);
            
            var json_champion;
            for (i = 0; i < json_all_champions.length; i++) {

                //then change the 'champion_select' function
                //then change champion_select() onclick
                json_champion = json_all_champions[i];

                id = json_champion[0];
                name = json_champion[1];
                icon = json_champion[2];

                champion = new Champion(id, name, icon);

                //Add champion into array with index as id
                all_champions[id] = champion;
                refine_champion_pool[id] = champion;

            }

            populate_div(refine_champion_pool);
        });


}

function populate_div(pool) {

    $('#champion_pool').empty();

    var champion;
    for (i = 0; i < 301; i++) {
        champion = pool[i];
        // console.log(champion);
        if (champion != undefined) {

            $( "#champion_pool" ).append( "<a onclick=champion_select(" + champion.champId + ")><img src=" + champion.champIcon + "></img></a>" );

        }
    }

}

function champion_select(id) {
    console.log("champion_selected: " + id);
    // $.ajax({
    //     type : "POST",
    //     url : '/select_champion/' + id + ''
    //     }).done(function(json_champion) {
            
    //         // console.log(json_champion)
    //         if (json_champion != "None") {

    //             // console.log("name.name: ", json_champion["name"]);
                
    //             id = json_champion["id"];
    //             name = json_champion["name"];
    //             icon = json_champion["icon"];

    //             champion = new Champion(id, name, icon);
    //             selected_array[id] = champion;
    //             // refined_array[id] = champion;

    //             $("#selected_pool").append("<a id=selected_" + id + " onclick=champion_deselect(" + id + ")><img src=" + icon + "></img></a>");
                
    //         }

    //     });

    champion = all_champions[id];
    id = champion.champId;
    icon = champion.champIcon;

    if (selected_array[id] == undefined) {
        selected_array[id] = champion;
        $("#selected_pool").append("<a id=" + id + " onclick=champion_deselect(" + id + ")><img src=" + icon + "></img></a>");

    }
    


}

function champion_deselect(id) {

    console.log("deselect js:", id);
    // $.ajax({
    //     type : "POST",
    //     url : '/deselect_champion/' + id + ''
    //     }).done(function(response) {
    //         if (response == "success") {

    //             delete selected_array[id];
    //             // delete refined_array[id];

    //             $("#selected_" + id + "").remove();

    //         }

    //     });

    selected_array[id] = undefined;
    $("#selected_pool #" + id + "").remove();
}

function random_champion() {
    //just get all existing id in 'selected_array' in a transient array then roll
    
    selected_div_champions = $("#selected_pool a");

    random_index = Math.floor(Math.random() * selected_div_champions.length);

    id = selected_div_champions[random_index].id;

    champion = selected_array[id];

    

    $("#random_roll").remove();
    $("#rolled_champion").append("<a id=random_roll><img style='width:15%;' src=" + champion.champIcon + "></img></a>");

    $('#roll_model').show();
    $("#roll_model").css("display", "block");

}


//on back space do another search
//when input field has nothing get all champions

// and just have all the refined id's returned by python
function refine_pool(query) {
    $.ajax({
        type : "GET",
        url : '/refine_pool/' + query + ''
        }).done(function(json_champion) {
            json_champion = JSON.parse(json_champion)
            console.log("input returned: " + json_champion);

            refine_champion_pool = [];

            var id;
            var champion;
            for (i = 0; i < json_champion.length; i++) {
                id = json_champion[i];
                champion = all_champions[id];

                refine_champion_pool[id] = champion;

            }

            populate_div(refine_champion_pool);
        });

}

//Admin section
function get_tags(id) {
    $('#tag_model').show();
    $("#tag_model").css("display", "block");
    
    $( "#tag_champion" ).empty();

    console.log("test get tags");

    $.ajax({
        type : "GET",
        url : '/get_tags/' + id + ''
        }).done(function(champion_tags) {
            json_tags = JSON.parse(champion_tags)
            console.log(json_tags);
            // id = id -1;
            $( "#tag_champion" ).append( "<button onclick='add_tag(" + id + ")' class='button5'>Add Tag</button>" );
            
            for (i = 0; i < json_tags.length; i++) {
                var tag_name = json_tags[i];
                $( "#tag_champion" ).append( "<a class='tag' onclick='remove_tag(" + id + ", " + JSON.stringify(tag_name) + ")'>" + tag_name + "</a>" );

            }

            
            
        });
}


function add_tag(id) {
    let tag_name = prompt('Type here');
    // let tag_name = confirm('Confirm or deny');
    console.log("tag name:" + tag_name + ", " + id);

    var query = id + tag_name;

    $.ajax({
        type : "POST",
        url : '/add_tag_route/' + query + ''
        }).done(function(champion_tags) {
            // json_tags = JSON.parse(champion_tags)
            // console.log(json_tags);
            
            console.log(champion_tags);
        });

    // $( "#tag_champion" ).empty();
    get_tags(id);
}


function update_modal_fill(id) {
    console.log("update modal fill");
    //get attributes of champ
    var champion_name = all_champions[id].champName;
    let champion_icon = all_champions[id].champIcon;

    // console.log(all_champions[1].champName);

    $("#update_champion_name").val(champion_name);
    $("#update_champion_icon").val(champion_icon);

}