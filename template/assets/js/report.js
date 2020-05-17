/* globals rt:false, feather:false */

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
    if (item !== "header" && item.substring(0, 3) !== "AF_") {
      list += `<li class="nav-item"><a id="menulink-${item}" class="nav-link menu-item" href="javascript:void(null);"><span data-feather="file-text"></span>${capitalize(item.replace("_", " "))}</a></li>`;
    }
  });
  $("#menu-list").html(list);

  list = "";

  Object.keys(reportData).forEach(function (item) {
    if (item !== "header" && item.substring(0, 3) !== "AF_") {
      list += `<li class="nav-item"><a id="menulink-${item}-listmobile" class="navbar-light nav-link menu-item top-link-mobile" style="padding: 0.5rem 0.8rem" href="javascript:void(null);"><span data-feather="file-text" class="mr-1"></span>${capitalize(item.replace("_", " "))}</a></li>`;
    }
  });

  $("#menu-list-mobile").html(list);
  $(".menu-item").on("click", menuClick);
}

function generatedDate() {
  let timestamp = new Date(reportData["header"]["report_date"]);
  let date = timestamp.toLocaleDateString("pt-PT");
  let time = timestamp.toLocaleTimeString("pt-PT");


  $("#generated-date").html("Generated at " + date + " " + time);
}

function onChangeMenu() {
  $("#page-builder").addClass("px-4");
  $('.navbar-collapse').collapse('hide');
}

function menuClick(event) {
  onChangeMenu()

  if (event.target) {
    idName = event.target.id.replace('-listmobile', '');
  }
  else {
    idName = "menulink-" + event.replace('-listmobile', '');
  }

  removeFocus()

  $("#" + idName).addClass("active");

  let name = idName.replace("menulink-", "")
  pageBuilder(name);
}

function renderMap() {
  if (reportData["AF_location"] == undefined) {
    $('#empty-map-modal').modal('show');
    return
  }

  onChangeMenu()
  $("#page-builder").removeClass("px-4");

  var content = `
    <div class="grid-container">
      <div class="grid-item map-style" id="map">
      </div>
    <div>
  `
  removeFocus()
  $("#page-builder").html(content);

  var map = L.map('map');

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    // attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  let markers = []

  reportData["AF_location"].forEach(item => {

    timestamp = new Date(item["timestamp"] * 1000);
    let date = timestamp.toLocaleDateString("pt-PT");
    let time = timestamp.toLocaleTimeString("pt-PT");

    popupContent = `
    <strong>Date:</strong> ${date}<br>
    <strong>Time:</strong> ${time}<br>
    <strong>Latitude:</strong> ${item["latitude"]}<br>
    <strong>Longitude:</strong> ${item["longitude"]}<br>
    `

    markers.push([item.latitude, item.longitude])
    L.marker([item["latitude"], item["longitude"]]).addTo(map)

      .bindPopup(popupContent)
      .openPopup();


  });

  map.fitBounds(markers);
  map.setZoom(13);
}

function renderTimeline() {
  if (reportData["AF_media"] == undefined) {
    $('#empty-media-modal').modal('show');
    return
  }
  onChangeMenu()
  removeFocus()

  content = getHeader("timeline")
  content += `<div class="tracking-list inline-block">`

  var id = 1
  var date = "";
  var time = "";
  var textclass = ""
  reportData["AF_timeline"].forEach(item => {
    date = "";
    time = "";
    textclass = ""
    if (item["timestamp"] == 0) {
      date = `Invalid date`
      time = `Invalid time`
      textclass = "text-danger"
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
          content += `<span><strong class="d-inline">${capitalize(body.replace("_", " "))} : </strong><div id='${"timeline-" + id}' class='collapse'> ${item["value"][body]}</div>
              <span class="d-inline btn btn-link text-primary" data-toggle="collapse" data-target="#${"timeline-" + id}">Expand/Collapse</span></span>`;
        } else {
          content += `<span><strong class="d-inline">${capitalize(body.replace("_", " "))} : </strong><div class="d-inline" id='${"timeline-" + id}'> ${item["value"][body]}</div></span>`;
        }

      } catch (error) {
        content += `<span><strong class="d-inline">${capitalize(body.replace("_", " "))} : </strong><div class="d-inline" id='${"timeline-" + id}'> ${item["value"][body]}</div></span>`;
      }

    });
    content += `</div></div>`

  });

  content += `</div></div></div>`
  $("#page-builder").html(content);

}

function getHeader(title) {
  return `<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"><h1 class="h2">${capitalize(title.replace("_", " "))}</h1></div>`
}

function removeFocus() {
  Object.keys(reportData).forEach(function (item) {
    $("#menulink-" + item).removeClass("active");
  });
}


function renderMedia() {

  //   content = `<div class="embed-responsive embed-responsive-21by9">
  //   <iframe class="embed-responsive-item" src="C:\\Users\\josef\\Desktop\\Autopsy_tests\\asdasd\\ModuleOutput\\AndroidForensics\\com.zhiliaoapp.musically\\2\\report\\Contents\\external\\cache\\welcome_screen_video4.mp4"></iframe>
  // </div>`;


  if (reportData["AF_media"] == undefined) {
    $('#empty-media-modal').modal('show');
    return
  }
  onChangeMenu()

  removeFocus()

  $("#page-builder").html("");


  // src = `C:\\Users\\josef\\Desktop\\ee\\test.mp4`
  // src2 = `C:\\Users\\josef\\Desktop\\ee\\test.jpg`
  var content = `
  ${getHeader("Media")}
  <div class="row">
  `

  var media_id = 0
  reportData["AF_media"].forEach(item => {
    if (item["type"] == "unknown") {
      return 
    }

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
    media_id += 1;
    content += `<div class="col mt-4 text-center" style="width:240px !important">`;

    if (item["type"] == "video") {
      content += `<video class="mb-3" width="240" controls><source src="${item["path"]}" type="${item["mime"]}"></video>`;
      content += `<button class="btn btn-sm"><img src="assets/svg/video.svg" alt="${item["mime"]}" class="minilogo"></img></button>`;
    } 
    else if (item["type"] == "image") {
      content += `<img width="240" class="img-responsive mb-3" src="${item["path"]}"></img>`;
      content += `<button class="btn btn-sm"><img src="assets/svg/image.svg" alt="${item["mime"]}" class="minilogo"></img> Image</button>`;
    }
    else if (item["type"] == "audio") {
      content += `<audio class="mb-3" controls><source src="${item["path"]}" type="${item["mime"]}"></audio>`;
      content += `<button class="btn btn-sm"><img src="assets/svg/audio.svg" alt="${item["mime"]}" class="minilogo"></img></button>`;
    }

    content += `<button type="button" class="btn btn-primary btn-sm button-copy" data-toggle="tooltip" data-placement="bottom" title="${item["path"]}">Copy Path</button>`;

    if (item["type"] === "video"){
      content += `<button type="button" class="btn btn-primary btn-sm" data-toggle="tooltip" data-placement="bottom" title="${item["path"]}">External Viewer</button>`
    }


    content += `</div>`


    // content += `
    // <div class="col-lg-4 col-md-12 mb-4">
    //   <div class="">
    //     <embed src="${item["path"]}" autostart="0"/></embed>
    //   </div>
    //   <span>Path:${item["path"]}</span>
    // </div>`

  });

  content += `</div>`;

  $("#page-builder").html(content);
  $(".button-copy").on("click", copyText);

}





function pageBuilder(title) {
  if (!(title in reportData)) {
    return;
  }

  let content = "";

  content += getHeader(title)

  //Array of objects
  if (Array.isArray(reportData[title]) && typeof reportData[title][0] === 'object') {
    let titleDefined = false;
    content += `<div class="table-responsive"><table class="table table-striped table-sm table-bordered table-hover">`;

    reportData[title].forEach(item => {
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
  else if (Array.isArray(reportData[title]) && typeof reportData[title][0] === 'string') {
    content += `<ul class="list-group">`;
    reportData[title].forEach(item => {
      content += `<li class="list-group-item">${JSON.stringify(item)}</li>`;
    });
    content += `</ul>`;
  }
  //Object (key/value)
  else if (typeof reportData[title] === 'object') {
    content += `<div class="table-responsive"><table class="table table-striped table-sm table-bordered table-hover">`;



    Object.keys(reportData[title]).forEach(function (key) {
      content += `<tr><td>${key}</td><td>${JSON.stringify(reportData[title][key])}</td></tr>`;
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

function copyText(event){
  //https://stackoverflow.com/a/30905277
  var $temp = $("<input>");
  $("body").append($temp);
  $temp.val(event.target.dataset.originalTitle).select();
  document.execCommand("copy");
  $temp.remove();
}

function makeReport() {
  onChangeMenu()

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

  //Tooltip hack
  $(document).ready(function() {
      $("body").tooltip({ selector: '[data-toggle=tooltip]' });
  });

  $("#timeline-btn").on("click", renderTimeline);
  $("#map-btn").on("click", renderMap);
  $("#media-btn").on("click", renderMedia);
  $("#pdf-btn").on("click", makeReport);
  feather.replace()
}())

