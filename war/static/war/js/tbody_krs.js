// var path = location.pathname;
// var directories = path.split("/");
// var lastDirecotry = directories[(directories.length - 1)];
// let URL = '/accounts/api/krs_war/' + lastDirecotry;
// Use global variable defined in template
let URL = krsApiUrl;

// POST SECTION
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

function submitForm(pk) {
    fetch(URL, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest', //Necessary to work with request.is_ajax()
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'pk': pk }) //JavaScript object of data to POST
    })
        .then(response => {
            return response.json() //Convert response to JSON
        })
        .then(data => {
            // divAlert = document.getElementById("alertMessage");
            // if (data['status'] == "limit") {
            //     window.scrollTo(0, 0);
            //     divAlert.classList.add("alert");
            //     divAlert.classList.add("alert-danger");
            //     divAlert.classList.remove("hidden");
            //     divAlert.innerText = data['message'];
            // } else {
            //     divAlert.classList.remove("alert");
            //     divAlert.classList.remove("alert-danger");
            //     divAlert.classList.add("hidden");
            //     divAlert.innerText = null;
            // };
            if (data['status'] == "limit") {
                window.alert([data['message']]);
            };

            generateTable();
            //Perform actions with the response data from the view
        });
};




// GET SECTION
function generateTable() {
    fetch(URL, {
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest', //Necessary to work with request.is_ajax()
        },
    })
        .then(response => {
            return response.json() //Convert response to JSON
        })
        .then(data => {
            //Perform actions with the response data from the view
            infoSelected = document.getElementById("infoSelected");
            if (data['schedule_name'] != null) {
                infoSelected.innerText = "Jadwal Praktikum Anda: " + data['schedule_name'];
            } else {
                infoSelected.innerText = "Anda belum memilih jadwal praktikum";
            };

            function removeAllChildNodes(parent) {
                while (parent.firstChild) {
                    parent.removeChild(parent.firstChild);
                }
            };
            let list = document.getElementById("tableList");
            removeAllChildNodes(list);

            let schedule = data['schedule'];
            let selected_pk = data['selected_pk'];
            for (i = 0; i < schedule.length; ++i) {
                let tr = document.createElement('tr');
                if (selected_pk === schedule[i]['pk']) {
                    tr.classList.add("active-row");
                };

                let td0 = document.createElement('td');
                td0.align = 'center';
                td0.innerText = i + 1;
                tr.appendChild(td0);

                let td1 = document.createElement('td');
                td1.innerText = schedule[i]['name'];
                tr.appendChild(td1);

                let td2 = document.createElement('td');
                td2.align = 'center';
                td2.innerText = schedule[i]['max_enrolled'];
                tr.appendChild(td2);

                let td3 = document.createElement('td');
                td3.align = 'center';
                td3.innerText = schedule[i]['available'];
                tr.appendChild(td3);

                let td4 = document.createElement('td');
                td4.align = 'center';
                let inpt = document.createElement('input');
                inpt.type = 'checkbox';
                inpt.name = 'pk';
                inpt.value = schedule[i]['pk'];
                inpt.alreadyChecked = false;
                if (selected_pk === schedule[i]['pk']) {
                    inpt.alreadyChecked = true;
                    inpt.checked = true;
                };
                inpt.addEventListener(
                    'change',
                    function () {
                        if (inpt.alreadyChecked) { // from checked to blank
                            submitForm(-1);
                        } else { // from blank to checked
                            submitForm(inpt.value);
                        };
                    },
                    false
                );
                td4.appendChild(inpt);
                tr.appendChild(td4);

                list.appendChild(tr);
            };
        });
};

generateTable();