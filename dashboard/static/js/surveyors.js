    function append_users_data(body, time, users) {
        //add first row with correct column span
        var row = $("<tr>");
        console.log(users);
        row.append($("<th>").text(time)
            .attr("rowspan", users.length)
        );
        row.append($("<td>").text(users[0].rte_desc)
            .attr("class", "text-center")
        );
        row.append($("<td>").text(users[0].user)
            .attr("class", "text-center")
        );
        body.append(row);
    
        //add rest of the data
        for(var i = 1; i < users.length; i++) {
            var row = $("<tr>");
            row.append($("<td>").text(users[i].rte_desc)
                .attr("class", "text-center")
            );
            row.append($("<td>").text(users[i].user)
                .attr("class", "text-center")
            );
            body.append(row);
        }
    }
    
    
    function rebuild_users(url, args) {
        $.getJSON(url, args, function(data) {
            var data = data.users;
            //clear table and rebuild with fetched json
            var body = $("#workers-table tbody");
            body.empty();
            $(times).each(function(index, item) {
                if(data.hasOwnProperty(item['id'])){
                    append_users_data(body, item['label'], data[item['id']]);
                }
                else {
                    var row = $("<tr>");
                    row.append($("<th>").text(item['label']));
                    row.append($("<td>")
                        .attr("colspan", 2)
                        .attr("class", "text-center status-none")
                    );
                    body.append(row);
                }
            });
        });
    }
 
    
    function get_date(today) {
        if(!today) today = new Date();
        var dd = today.getDate();
        var mm = today.getMonth()+1; //January is 0!
        var yyyy = today.getFullYear();

        if(dd < 10) {
            dd='0'+dd
        } 
        if(mm < 10) {
            mm='0'+mm
        } 
        return mm + '-' + dd + '-' + yyyy;
    }
    
    var url = "surveyors/_summary";
    var times = [
        {'id':'AM Peak', 'label':'AM Peak - 6:00 am to 8:59 am'},
        {'id':'Midday', 'label':'Midday - 9:00 am to 3:59 pm'},
        {'id':'PM Peak', 'label':'PM Peak - 4:00 pm to 6:59 pm'},
        {'id':'Evening', 'label':'Evening - 7:00 pm to 10:00 pm'}
    ];

    $("#date-select").val(get_date());
    //build table for today
    rebuild_users(url, {'date':get_date()});

    $("#date-select").datepicker({
        dateFormat: "mm-dd-yy",
        autoclose:true,
        onSelect: function(sel_date, dp) {
            console.log("selected date");
            console.log(sel_date);
            rebuild_users(url, {'date':sel_date});
        }
    });