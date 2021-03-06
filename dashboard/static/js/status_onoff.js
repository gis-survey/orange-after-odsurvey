    function build_cell(text, pct) {
        var td = $('<td>');
        //td.text(text);
        if(pct) {
            //if(pct > 100) text = "100%";
            //else text = pct.toString() + "%";
            text = pct.toString() + "%";
        td.attr("class", get_status(pct));
        }
        if(text == 'N/A') {
            td.attr("class", "status-none");
        }
        td.text(text);
        td.attr("align", "center");
        return td;
    }
    
    function get_number(data) {
        var ret_val = "";
        if(!$.isEmptyObject(data)) {
            ret_val = (data['count'].toString() + '/' + data['target'].toString())
        }
        return ret_val;
    }

    function get_pct(data) {
        var ret_val = 0;
        if(!$.isEmptyObject(data)) {
            ret_val= ((data['count'] / data['target']) * 100).toFixed(0);
        }
        return ret_val;
    }

    function get_status(pct_complete) {
        var cls = "";
        switch (Math.floor(pct_complete / 25) + 1) {
            //0% -> 24%
            case 1:
                cls = "status-1";
                break;
            //25% -> 49%  
            case 2:
                cls = "status-2";
                break;
            //50% -> 74%    
            case 3:
                cls = "status-3";
                break;
            //75% -> 99%    
            case 4: 
                cls = "status-4";
                break;
            //100% +    
            default:
                cls = "status-complete";
        }
        return cls;
    }
    
    function build_stats_row(rte_desc, data, summary_data) {
        var array = [];
        var nbsp = "N/A";
        array[0] = rte_desc
       
        var tr = $('<tr>');
            tr.append($('<th>').text(rte_desc));
            tr.append(build_cell(get_number(summary_data), get_pct(summary_data))); 
        
        for(var i = 0; i < 4; i++) {
            if (!$.isEmptyObject(data['1'][times[i]])) {
                tr.append(
                    build_cell(
                        get_number(data['1'][times[i]]),
                        get_pct(data['1'][times[i]])
                    )
                );
            }
            else {
                tr.append(build_cell(nbsp, null));
            }   
        }
        for(var i = 4; i < 8; i++) {
            if (!$.isEmptyObject(data['0'][times[i - 4]])) {
                tr.append(
                    build_cell(
                        get_number(data['0'][times[i - 4]]),
                        get_pct(data['0'][times[i - 4]])
                    )
                );
            }
            else {
                tr.append(build_cell(nbsp, null));
            }
        }
        return tr;
    }
    

    var times = ['AM Peak', 'Midday', 'PM Peak', 'Evening'];

    $(routes).each(function(index, item) {

        var tr = $('<tr>');
        if (item.indexOf('Portland Streetcar') < 0) {
            tr = build_stats_row(item, data[item], summary[item]);
        }
        else {
            tr.append($('<th>').text(item));
            tr.append(
                $('<td>').text(get_pct(streetcar[item]).toString() + '%')
                    .attr("colspan", "9")
                    .attr("class", get_status(get_pct(streetcar[item])))
                    .attr("align", "center")
            );
        }
        $("#status-table tbody").append(tr);
    
    });