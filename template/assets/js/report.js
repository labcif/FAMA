/* globals Chart:false, feather:false */

function capitalize(text) {
  return text.charAt(0).toUpperCase() + text.substr(1).toLowerCase();
}

function initializeMenus() {
  let info = `<div><strong>Report:</strong> ${reportData.header.report_name}</div>
  <div><strong>App:</strong> ${capitalize(reportData.header.app_name)} (${reportData.header.app_id})</div>`

  if (reportData.header.case_name) {
    info += `<div><strong>Case:</strong> ${reportData.header.case_name}</div>`
  }

  if (reportData.header.case_number) {
    info += `<div><strong>Nº:</strong> ${reportData.header.case_number}</div>`
  }

  if (reportData.header.examiner) {
    info += `<div><strong>Examiner:</strong> ${reportData.header.examiner}</div>`
  }

  $("#report-info").html(info);

  let list = "";

  Object.keys(reportData).forEach(function (item) {
    if (item !== "header" && item.substring(0, 3) !=="AF_") {
      list += `<li class="nav-item"><a id="menulink-${item}" class="nav-link menu-item" href="javascript:void(null);"><span data-feather="file-text"></span>${capitalize(item.replace("_", " "))}</a></li>`;
    }
  });
  $("#menu-list").html(list);
  $(".menu-item").on("click", menuClick);
}

function generatedDate() {
    let timestamp = new Date(reportData["header"]["report_date"]);
    let date = timestamp.toLocaleDateString("pt-PT");
    let time = timestamp.toLocaleTimeString("pt-PT");


  $("#generated-date").html("Generated at " + date + " " + time);
}

function extraButtons() {

}

function menuClick(event) {
  if (event.target) {
    idName = event.target.id;
  }
  else {
    idName = "menulink-" + event;
  }

  removeFocus()

  $("#" + idName).addClass("active");

  let name = idName.replace("menulink-", "")
  pageBuilder(name);
}

function renderMap() {
  if (report["AF_location"] == undefined) {
    $('#empty-map-modal').modal('show');
    return
  }

  var content = `
    <div style="height:auto;width:auto;" class="grid-container">
      <div style="height: calc(100vh - 48px);width:100%; display:block" class="grid-item" id="map">
      
  
      </div>
    <div>
  `
  removeFocus()
  $("#page-builder").html(content);

  var map = L.map('map').setView([report["AF_location"][0]["latitude"], report["AF_location"][0][["longitude"]]], 13);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    // attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  report["AF_location"].forEach(item => {

    timestamp = new Date(item["timestamp"] * 1000);
    let date = timestamp.toLocaleDateString("pt-PT");
    let time = timestamp.toLocaleTimeString("pt-PT");

    popupContent = `
    <strong>Date:</strong> ${date}<br>
    <strong>Time:</strong> ${time}<br>
    <strong>Latitude:</strong> ${item["latitude"]}<br>
    <strong>Longitude:</strong> ${item["longitude"]}<br>
    `


    L.marker([item["latitude"], item["longitude"]]).addTo(map)

      .bindPopup(popupContent)
      .openPopup();


  });



}

function renderTimeline() {
  if (report["AF_timeline"] == undefined) {
    $('#empty-timeline-modal').modal('show');
    return
  }

  removeFocus()

  content = getHeader("timeline")

  content += `<div class="row"><div class="tracking-list">`

  var id = 1

  reportData["AF_timeline"].forEach(item => {
    let date = "";
    let time = "";
    let textclass = ""
    if (item["timestamp"] == 0) {
      date = `Invalid date`
      time = `Invalid time`
      textclass= "text-danger"
    } else {
      timestamp = new Date(item["timestamp"] * 1000);
      date = timestamp.toLocaleDateString("pt-PT");
      time = timestamp.toLocaleTimeString("pt-PT");
    }

    content += ` <div class="tracking-item">
        <div class="tracking-icon status-intransit"> 
        <object data="assets/svg/${item["event"]}.svg" type="image/svg+xml" class="w-100"}"></object>
        
        </div>
        <div class="tracking-date ${textclass}">${date}<span class="${textclass}">${time}</span></div>
        <div class="tracking-content">`

    id += 1
    Object.keys(item["value"]).forEach(function (body) {
      id += 1
      try {
        if (item["value"][body].length > 100) {
          content += `<span><strong class="d-inline">${body} : </strong><div id='${"timeline-" + id}' class='collapse'> ${item["value"][body]}</div>
              <span class="d-inline btn btn-link text-primary" data-toggle="collapse" data-target="#${"timeline-" + id}">Expand/Collapse</span></span>`;
        } else {
          content += `<span><strong class="d-inline">${body} : </strong><div class="d-inline" id='${"timeline-" + id}'> ${item["value"][body]}</div></span>`;
        }
      
      } catch (error) {
        content += `<span><strong class="d-inline">${body} : </strong><div class="d-inline" id='${"timeline-" + id}'> ${item["value"][body]}</div></span>`;
      }

    });
    content += `</div></div>`

  });

  content += `</div></div></div></div>`
  $("#page-builder").html(content);

}

function getHeader(title) {
  return `<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"><h1 class="h2">${capitalize(title.replace("_", " "))}</h1></div>`
}

function removeFocus(){
  Object.keys(reportData).forEach(function (item) {
    $("#menulink-" + item).removeClass("active");
  });
}


function renderMedia() {
  //   content = `<div class="embed-responsive embed-responsive-21by9">
  //   <iframe class="embed-responsive-item" src="C:\\Users\\josef\\Desktop\\Autopsy_tests\\asdasd\\ModuleOutput\\AndroidForensics\\com.zhiliaoapp.musically\\2\\report\\Contents\\external\\cache\\welcome_screen_video4.mp4"></iframe>
  // </div>`;


  if (report["AF_media"] == undefined) {
    $('#empty-media-modal').modal('show');
    return
  }

  removeFocus()

  $("#page-builder").html("");


  // src = `C:\\Users\\josef\\Desktop\\ee\\test.mp4`
  // src2 = `C:\\Users\\josef\\Desktop\\ee\\test.jpg`
  content = `
  ${getHeader("Media")}
  <div class="row">
  `
  report["AF_media"].forEach(item => {
    // content += `
    // <div class="col-lg-4 col-md-12 mb-4">
    //   <div class="embed-responsive embed-responsive-4by3 z-depth-1-half">
    //     <iframe src="${item}" allowfullscreen></iframe>
    //   </div>
    //   <span>${item}<span>
    // </div>`

    // content += `
    // <div class="col-lg-4 col-md-12 mb-4">
    //   <div class="embed-responsive embed-responsive-4by3 z-depth-1-half">
    //   <video width="320" height="240" controls>
    //     <source src="${item}" type="video/mp4">
    //   Doest support video
    // </video>
    // <img src="${item}" alt="">
    //   </div>
    //   <span>${item}</span>
    // </div>`

    content += `
    <div class="col-lg-4 col-md-12 mb-4">
      <div class="">
      
    
        <embed src="${item}" autostart="0"/></embed>
      
      </div>
      <span>${item}</span>
    </div>`

  });

  content += `</div>`

  $("#page-builder").html(content);

}


function pageBuilder(title) {
  report = reportData
  if (!(title in report)) {
    return;
  }

  let content = "";

  content += getHeader(title)

  //Array of objects
  if (Array.isArray(report[title]) && typeof report[title][0] === 'object') {
    let titleDefined = false;
    content += `<div class="table-responsive"><table class="table table-striped table-sm table-bordered table-hover">`;

    report[title].forEach(item => {
      //define table header
      if (!titleDefined) {
        let theads = ""
        Object.keys(item).forEach(function (head) {
          theads += `<td>${head}</td>`;
        });
        titleDefined = true;

        content += `<thead><tr>${theads}</tr></thead><tbody>`
      }

      content += `<tr>`;
      Object.keys(item).forEach(function (body) {
        content += `<td>${JSON.stringify(item[body])}</td>`;
      });
      content += `</tr>`;
    })

    content += `</tbody></table></div>`;
  }
  //Array of strings
  else if (Array.isArray(report[title]) && typeof report[title][0] === 'string') {
    content += `<ul class="list-group">`;
    report[title].forEach(item => {
      content += `<li class="list-group-item">${JSON.stringify(item)}</li>`;
    });
    content += `</ul>`;
  }
  //Object (key/value)
  else if (typeof report[title] === 'object') {
    content += `<div class="table-responsive"><table class="table table-striped table-sm table-bordered table-hover">`;



    Object.keys(report[title]).forEach(function (key) {
      content += `<tr><td>${key}</td><td>${JSON.stringify(report[title][key])}</td></tr>`;
    });

    content += `</tbody></table></div>`;

  }

  $("#page-builder").html(content);
}

function startUp() {
  initializeMenus()
  generatedDate()

  let defined = false
  Object.keys(reportData).forEach(function (item) {
    if (!defined && item !== "header") {
      menuClick(item);
      defined = true;
    }
  });

  feather.replace()
}

function makeReport() {
  $('#loading-modal').modal('show');
  setTimeout(function () {
    content = [
      {
        text: `LabCIF - Android Forensics Report`,
        style: 'header'
      },
      {
        text: `${capitalize(reportData.header.app_name)} - Report ${reportData.header.report_name}`,
        style: 'subheader',
        margin: [0, 0, 0, 20]
      },
    ]

    if (reportData.header.case_name) {
      content.push({
        text: `Case Name: ${reportData.header.case_name}`
      });
    }

    if (reportData.header.case_number) {
      content.push({
        text: `Case Number: ${reportData.header.case_number}`
      })
    }

    if (reportData.header.examiner) {
      content.push({
        text: `Examiner: ${reportData.header.examiner}`,
        margin: [0, 0, 0, 20]
      })
    }

    Object.keys(reportData).forEach(function (key) {
      if (key === "header") {
        return
      }

      content.push({
        text: `Category: ${capitalize(key)}`,
        style: 'subheader'
      })

      rows = []

      if (Array.isArray(reportData[key]) && typeof reportData[key][0] === 'object') {
        let titleDefined = false;
        reportData[key].forEach(item => {
          //define table header
          if (!titleDefined) {
            let header = []

            Object.keys(item).forEach(function (head) {
              header.push(head)
            });

            titleDefined = true;
            rows.push(header)
          }

          let individual = []
          Object.keys(item).forEach(function (body) {
            individual.push(JSON.stringify(item[body]));
          });

          rows.push(individual);
        })

      }
      //Array of strings
      else if (Array.isArray(reportData[key]) && typeof reportData[key][0] === 'string') {
        reportData[key].forEach(item => {
          rows.push([item]);
        });
      }
      //Object (key/value)
      else if (typeof reportData[key] === 'object') {
        Object.keys(reportData[key]).forEach(function (item) {
          rows.push([item, JSON.stringify(reportData[key][item])]);
        });
      }


      if (rows.length > 0) {
        content.push({
          style: 'tableExample',
          table: {
            body: rows
          }
        })
      }

      // text = [
      //   'It is however possible to provide an array of texts ',
      //   'to the paragraph (instead of a single string) and have ',
      //   {text: 'a better ', fontSize: 15, bold: true},
      //   'control over it. \nEach inline can be ',
      //   {text: 'styled ', fontSize: 20},
      //   {text: 'independently ', italics: true, fontSize: 40},
      //   'then.\n\n'
      // ]

      //content.push(text)
    });

    var docDefinition = {
      content: content,
      styles: {
        header: {
          fontSize: 18,
          bold: true
        },
        subheader: {
          fontSize: 15,
          bold: true
        },
        quote: {
          italics: true
        },
        small: {
          fontSize: 8
        },
        tableExample: {
          margin: [0, 5, 0, 15],
          width: 50
        },
      }
    };
    pdfMake.createPdf(docDefinition).download(`Report_${reportData.header.app_name}_${reportData.header.report_name}.pdf`);
    $('#loading-modal').modal('hide');
  }, 50);
}

(function () {
  'use strict'
  startUp()

  $("#timeline-btn").on("click", renderTimeline);
  $("#map-btn").on("click", renderMap);
  $("#media-btn").on("click", renderMedia);
  $("#pdf-btn").on("click", makeReport);
  feather.replace()
}())

