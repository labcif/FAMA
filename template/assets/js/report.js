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

  let indexnumber = 0;
  Object.keys(reportData).forEach(function (item) {
    indexnumber += 1;
    if (item !== "header" && item.substring(0, 3) !== "AF_") {
      list += `<li class="nav-item"><a id="menulink-${indexnumber}" class="nav-link menu-item" href="javascript:void(null);"><span data-feather="file-text"></span>${capitalize(item.replace("_", " "))}</a></li>`;
    }
  });
  $("#menu-list").html(list);

  list = "";

  indexnumber = 0;
  Object.keys(reportData).forEach(function (item) {
    indexnumber += 1;
    if (item !== "header" && item.substring(0, 3) !== "AF_") {
      list += `<li class="nav-item"><a id="menulink-${indexnumber}-listmobile" class="navbar-light nav-link menu-item top-link-mobile" style="padding: 0.5rem 0.8rem" href="javascript:void(null);"><span data-feather="file-text" class="mr-1"></span>${capitalize(item.replace("_", " "))}</a></li>`;
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
    idName = "menulink-" + event.toString().replace('-listmobile', '');
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
  let indexnumber = 0;
  Object.keys(reportData).forEach(function (item) {
    indexnumber += 1;
    $("#menulink-" + indexnumber).removeClass("active");
  });
}


function renderMedia() {
  if (reportData["AF_media"] == undefined) {
    $('#empty-media-modal').modal('show');
    return
  }
  onChangeMenu()

  removeFocus()

  $("#page-builder").html("");

  // src = `C:\\Users\\josef\\Desktop\\ee\\test.mp4`
  // src2 = `C:\\Users\\josef\\Desktop\\ee\\test.jpg`
  
  let content = `${getHeader("Media")}`
  
  content += `<div class="row"><div class="col-12"><strong>Filter:</strong>
    <select id="media-filter" class="form-control form-control-sm">
      <option value="all">📚 All</option>
      <option value="audio">🎧 Audios</option>
      <option value="image">🖼️ Images</option>
      <option value="video">🎥 Videos</option>
    </select>
  </div></div>`

  content += `<div id="media-list" class="row">`

  content += `</div>`;

  $("#page-builder").html(content);
  $(".button-copy").on("click", copyText);

  renderMediaList("all")

  $('#media-filter').on('change', function() {
    renderMediaList(this.value)
  });

}

function renderMediaList(filter){
  let mediaListing = ""
  reportData["AF_media"].forEach(item => {
    if (item["type"] == "unknown") {
      return 
    }

    mediaListing += `<div class="col mt-4 text-center lazy" style="width:240px !important">`;

    if (item["type"] == "video" && (filter === "all" || filter === "video")) {
      mediaListing += `<video class="mb-3 lazy" poster="assets/img/external.png" width="240" height="380" controls autoplay muted><source src="${item["path"]}"></video>`;
      mediaListing += `<button class="btn btn-sm"><img src="assets/svg/video.svg" class="minilogo"/> Video</button>`;
    } 
    else if (item["type"] == "image" && (filter === "all" || filter === "image")) {
      mediaListing += `<img width="240" class="img-responsive mb-3 lazy" data-src="${item["path"]}"/>`;
      mediaListing += `<button class="btn btn-sm"><img src="assets/svg/image.svg" class="minilogo"/> Image</button>`;
    }
    else if (item["type"] == "audio" && (filter === "all" || filter === "audio")) {
      mediaListing += `<audio class="mb-3 lazy" controls><source data-src="${item["path"]}"></audio>`;
      mediaListing += `<button class="btn btn-sm"><img src="assets/svg/audio.svg" class="minilogo"/> Audio</button>`;
    }
    else{
      return
    }

    mediaListing += `<button type="button" class="btn btn-primary btn-sm button-copy" data-toggle="tooltip" data-placement="bottom" onclick='copyToClipboard("${item["path"]}")' title="${item["path"]}">Copy Path</button>`;

    if ((item["type"] === "video" && (filter === "all" || filter === "video")) || (item["type"] === "audio"  && (filter === "all" || filter === "video"))){
      mediaListing += `<a class="btn btn-primary btn-sm ml-2" href="${item["path"]}" download target="_blank">Download for External Player</a>`
    }

    mediaListing += `</div>`
  });

  $("#media-list").html(mediaListing);
  
  $(function($) {
    $(".lazy").Lazy('av', ['audio', 'img','video'], function(element, response) {
      // this plugin will automatically handle '<audio>' and '<video> elements,
      // even when no 'data-loader' attribute was set on the elements
    });
  });
  return mediaListing
}


function copyToClipboard(str) {
  const el = document.createElement('input');
  el.value = str;
  document.body.appendChild(el);
  el.select();
  document.execCommand('copy');
  document.body.removeChild(el);
};



function pageBuilder(titlenumber) {
  //if (!(title in reportData)) {
  //  return;
  //}
  let title = null;
  let indexnumber = 0;
  Object.keys(reportData).forEach(function (item) {
    indexnumber += 1;
    if (indexnumber == titlenumber){
      title = item
    }
  });

  if (!title){
    return
  }
  let content = "";

  content += getHeader(title)

  //Array of objects
  if (Array.isArray(reportData[title]) && typeof reportData[title][0] === 'object') {
    let titleDefined = false;
    content += `<div class="table-responsive"><table class="table table-striped table-sm table-bordered table-hover">`;

    reportData[title].forEach(item => {
      try {
        if (title === "messages" && item["messages"]){ //quick fix
          if (!titleDefined) {
            let title = ["participant_1", "participant_2", "createdtime", "readstatus","localinfo","sender","receiver","type","message","deleted"]
            let theads = ""
            Object.values(title).forEach(function (head) {
              theads += `<td>${head}</td>`;
            });
            titleDefined = true;

            content += `<thead><tr>${theads}</tr></thead><tbody>`
          }
          Object.values(item["messages"]).forEach(function (body) {
            content += `<tr>`;
            content += `<td>${JSON.stringify(item["participant_1"])}</td>`;
            content += `<td>${JSON.stringify(item["participant_2"])}</td>`;
            Object.values(body).forEach(function (messageitem) {
              content += `<td>${JSON.stringify(messageitem)}</td>`;
            });
            content += `</tr>`;
          });
          return
        }
      } catch (error) {
        
      }

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
  let indexnumber = 0
  Object.keys(reportData).forEach(function (item) {
    indexnumber += 1
    if (!defined && item !== "header") {
      menuClick(indexnumber);
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
          try {
            if (key === "messages" && item["messages"]){ //quick fix
              if (!titleDefined) {
                let header = ["participant_1", "participant_2", "createdtime", "readstatus","sender","receiver","type","message","deleted"]
                titleDefined = true;
                rows.push(header)
              }
              Object.values(item["messages"]).forEach(function (body) {
                let content = []
                content.push(item["participant_1"])
                content.push(item["participant_2"])

                Object.keys(body).forEach(function (messageitem) {
                  if (messageitem == "localinfo"){
                    return
                  }

                  content.push(body[messageitem])
                });
                rows.push(content);
              });
              return
            }
          } catch (error) {
            
          }
          
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
      pageOrientation: 'landscape',
      styles: {
        header: {
          fontSize: 14,
          bold: true
        },
        subheader: {
          fontSize: 12,
          bold: true
        },
        quote: {
          italics: true
        },
        small: {
          fontSize: 8
        },
        tableExample: {
          fontSize: 8,
          margin: [0, 5, 0, 15]
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

