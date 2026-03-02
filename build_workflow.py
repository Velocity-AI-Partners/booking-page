import json

format_email_code = """const booking = $json.body;

const name = booking.name || 'Customer';
const email = booking.email || '';
const phone = booking.phone || '';

const subject = `New Booking Request: ${name} - ${booking.date} at ${booking.time}`;

const htmlBody = `
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
  <div style="background: linear-gradient(135deg, #FF9900, #FF6D00); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center;">
    <h1 style="margin: 0; font-size: 20px;">New Booking Request</h1>
    <p style="margin: 5px 0 0; opacity: 0.9; font-size: 14px;">${booking.locationName || booking.location}</p>
  </div>
  <div style="border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 8px 8px; padding: 20px;">
    <table style="width: 100%; border-collapse: collapse;">
      <tr style="border-bottom: 1px solid #f3f4f6;">
        <td style="padding: 12px 8px; font-weight: bold; color: #6b7280; width: 120px;">Customer</td>
        <td style="padding: 12px 8px; font-weight: 600;">${name}</td>
      </tr>
      <tr style="border-bottom: 1px solid #f3f4f6;">
        <td style="padding: 12px 8px; font-weight: bold; color: #6b7280;">Email</td>
        <td style="padding: 12px 8px;"><a href="mailto:${email}">${email || 'N/A'}</a></td>
      </tr>
      <tr style="border-bottom: 1px solid #f3f4f6;">
        <td style="padding: 12px 8px; font-weight: bold; color: #6b7280;">Phone</td>
        <td style="padding: 12px 8px;"><a href="tel:${phone}">${phone}</a></td>
      </tr>
      <tr style="border-bottom: 1px solid #f3f4f6;">
        <td style="padding: 12px 8px; font-weight: bold; color: #6b7280;">Date</td>
        <td style="padding: 12px 8px; font-weight: 600;">${booking.date}</td>
      </tr>
      <tr style="border-bottom: 1px solid #f3f4f6;">
        <td style="padding: 12px 8px; font-weight: bold; color: #6b7280;">Time</td>
        <td style="padding: 12px 8px; font-weight: 600;">${booking.time}</td>
      </tr>
      ${booking.instructor ? '<tr style="border-bottom: 1px solid #f3f4f6;"><td style="padding: 12px 8px; font-weight: bold; color: #6b7280;">Instructor</td><td style="padding: 12px 8px;">' + booking.instructor + '</td></tr>' : ''}
      ${booking.className ? '<tr style="border-bottom: 1px solid #f3f4f6;"><td style="padding: 12px 8px; font-weight: bold; color: #6b7280;">Session Type</td><td style="padding: 12px 8px;">' + booking.className + '</td></tr>' : ''}
      ${booking.notes ? '<tr style="border-bottom: 1px solid #f3f4f6;"><td style="padding: 12px 8px; font-weight: bold; color: #6b7280;">Notes</td><td style="padding: 12px 8px;">' + booking.notes + '</td></tr>' : ''}
    </table>
    <div style="margin-top: 20px; padding: 16px; background: #FFF7ED; border: 1px solid #FF9900; border-radius: 8px;">
      <p style="margin: 0; font-size: 14px; font-weight: 600; color: #B45309;">Action Required</p>
      <p style="margin: 6px 0 0; font-size: 14px; color: #92400E;">Please confirm this booking with the customer at <a href="tel:${phone}" style="color: #B45309; font-weight: 600;">${phone}</a>.</p>
    </div>
    <div style="margin-top: 12px; padding: 12px; background: #f8fafc; border-radius: 6px; font-size: 12px; color: #9ca3af;">
      <p style="margin: 0;">Location: ${booking.locationName} | CRM: ${booking.crm || 'N/A'}${booking.leadId ? ' | Lead ID: ' + booking.leadId : ''}</p>
      <p style="margin: 4px 0 0;">Submitted via Velocity AI Booking Page</p>
    </div>
  </div>
</div>`;

const toEmail = booking.locationEmail || 'bjordan@velocityaipartners.ai';

return [{ json: { toEmail, subject, htmlBody } }];"""

prepare_scrape_code = """const body = $json.body;
const location = body.location || '';
const dateStr = body.date || '';
const storeId = body.storeId || 0;

// Route 1: Stretch Zone locations use knetk.io scraping
const knetkLocations = {
  'stretch-zone-westborough': { leadId: '128047422', storeId: 15077 },
  'stretch-zone-west-boylston': { leadId: '128181157', storeId: 14803 },
  'stretch-zone-dfw': { leadId: '128183277', storeId: 0 },
  'stretch-zone-baton-rouge': { leadId: '128122536', storeId: 0 },
};

const knetk = knetkLocations[location];
if (knetk) {
  const lid = body.leadId || knetk.leadId;
  const sid = storeId || knetk.storeId;
  const url = `https://stretchzone.knetk.io/${lid}/${sid}/39/locationformbooking`;
  return [{ json: { url, date: dateStr, location, storeId: sid, scrapeMode: 'knetk' } }];
}

// Route 2: StretchLab Carlsbad uses Xponential public API (live availability)
if (location === 'stretchlab-carlsbad') {
  const url = `https://members.stretchlab.com/api/locations/stretchlab-carlsbad-north-coast/service_types/24730?date=${dateStr}`;
  return [{ json: { url, date: dateStr, location, storeId: 0, scrapeMode: 'carlsbad' } }];
}

// Route 3: IMA locations use static schedules (handled client-side, but fallback here)
return [{ json: { url: '', date: dateStr, location, storeId: 0, scrapeMode: 'static' } }];"""

parse_slots_code = """const httpData = $input.first().json;
const prepData = $('Prepare Scrape').first().json;
const dateStr = prepData.date;
const location = prepData.location;
const scrapeMode = prepData.scrapeMode || 'knetk';

// Route 1: knetk.io HTML parsing (Stretch Zone locations)
if (scrapeMode === 'knetk') {
  const html = typeof httpData === 'string' ? httpData : (httpData.data || '');

  const regex = /onclick="\\$\\('#scheduledOn'\\)\\.val\\('(\\d{2}\\/\\d{2}\\/\\d{4} \\d{2}:\\d{2}:\\d{2})_(\\d+)_([\\d\\/ :]+)_([^']+)'\\); bookclass\\(\\);"[\\s\\S]*?<p>(.*?)<\\/p>[\\s\\S]*?<span>(.*?)<\\/span>/g;

  let match;
  const allSlots = [];

  while ((match = regex.exec(html)) !== null) {
    const [_, endTime, classId, startTime, fullName, displayTime, shortName] = match;
    const parts = startTime.split(' ')[0].split('/').map(Number);
    allSlots.push({
      month: parts[0], day: parts[1], year: parts[2],
      time: displayTime.trim(),
      instructor: fullName.trim(),
    });
  }

  const d = new Date(dateStr + 'T12:00:00');
  const slots = allSlots
    .filter(s => s.month === d.getMonth()+1 && s.day === d.getDate() && s.year === d.getFullYear())
    .map(s => ({ time: s.time, type: 'Stretch Session', instructor: s.instructor }));

  if (slots.length > 0) {
    return [{ json: { slots } }];
  }
}

// Route 2: Xponential API JSON parsing (StretchLab Carlsbad)
if (scrapeMode === 'carlsbad') {
  try {
    const data = typeof httpData === 'string' ? JSON.parse(httpData) : httpData;
    const entries = data.schedule_entries || [];
    const instructors = (data.service_type?.instructors || []);

    // Build instructor ID -> display name map
    const instMap = {};
    for (const inst of instructors) {
      instMap[inst.id] = inst.name || inst.id.split('-').pop();
    }

    if (entries.length > 0) {
      // Deduplicate: one slot per time PER duration type, first instructor wins
      const seen = {};
      for (const e of entries) {
        const dur = e.service_duration?.duration_minutes || 50;
        const startTime = e.starts_at || '';
        const instName = instMap[e.instructor_id] || e.instructor_id.split('-').pop();

        let displayTime = startTime;
        const tMatch = startTime.match(/T(\\d{2}):(\\d{2})/);
        if (tMatch) {
          const h = parseInt(tMatch[1]);
          const m = tMatch[2];
          const h12 = h > 12 ? h - 12 : (h === 0 ? 12 : h);
          const ampm = h >= 12 ? 'PM' : 'AM';
          displayTime = h12 + ':' + m + ' ' + ampm;
        }

        const key = displayTime + '|' + dur;
        if (!seen[key]) {
          seen[key] = {
            time: displayTime,
            type: dur + ' Min Stretch',
            instructor: instName,
            duration: dur,
            sortKey: startTime
          };
        }
      }

      const slots = Object.values(seen)
        .sort((a, b) => a.sortKey.localeCompare(b.sortKey))
        .map(({ time, type, instructor, duration }) => ({ time, type, instructor, duration }));

      if (slots.length > 0) {
        return [{ json: { slots } }];
      }
    }
  } catch (e) {
    // Fall through to static fallback
  }
}

// Static fallback: location-specific business hours
const hours = {
  'stretch-zone-westborough': { weekday: [8,19], sat: [10,15], sun: null, label: 'Stretch Session' },
  'stretch-zone-west-boylston': { weekday: [8,19], sat: [10,15], sun: null, label: 'Stretch Session' },
  'stretchlab-carlsbad': { weekday: [9,20], sat: [9,15], sun: [10,14], label: 'Stretch Session' },
  'stretch-zone-dfw': { weekday: [7,20], sat: [8,16], sun: [11,17], label: 'Stretch Session' },
  'stretch-zone-baton-rouge': { weekday: [8,19], sat: [10,16], sun: null, label: 'Stretch Session' },
};

const d2 = new Date(dateStr + 'T12:00:00');
const h = hours[location];
if (!h) return [{ json: { slots: [] } }];

const dow = d2.getDay();
const range = dow === 0 ? h.sun : dow === 6 ? h.sat : h.weekday;
if (!range) return [{ json: { slots: [] } }];

const fallback = [];
for (let hr = range[0]; hr < range[1]; hr++) {
  const h12 = hr > 12 ? hr - 12 : (hr === 0 ? 12 : hr);
  const ampm = hr >= 12 ? 'PM' : 'AM';
  fallback.push({ time: `${h12}:00 ${ampm}`, type: h.label });
}

return [{ json: { slots: fallback } }];"""

workflow = {
    "name": "Booking Page",
    "nodes": [
        {
            "parameters": {
                "path": "0c41acc9-33d5-467e-9182-6f39ceaa9a8e",
                "httpMethod": "POST",
                "responseMode": "responseNode",
                "options": {}
            },
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2.1,
            "position": [0, 0],
            "id": "c0eff6c2-e8e4-40b6-9c6b-cfefd363106f",
            "name": "Booking Submit",
            "webhookId": "c0eff6c2-e8e4-40b6-9c6b-cfefd363106f"
        },
        {
            "parameters": {
                "respondWith": "json",
                "responseBody": "={\"success\": true, \"message\": \"Booking request received\"}",
                "options": {}
            },
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1.1,
            "position": [260, 160],
            "id": "a1b2c3d4-0001-4000-a000-000000000001",
            "name": "Respond Success"
        },
        {
            "parameters": {
                "jsCode": format_email_code
            },
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [740, -100],
            "id": "a1b2c3d4-0002-4000-a000-000000000002",
            "name": "Format Booking Email"
        },
        {
            "parameters": {
                "sendTo": "={{ $json.toEmail }}",
                "subject": "={{ $json.subject }}",
                "emailType": "html",
                "message": "={{ $json.htmlBody }}",
                "options": {}
            },
            "type": "n8n-nodes-base.gmail",
            "typeVersion": 2.1,
            "position": [980, -100],
            "id": "a1b2c3d4-0003-4000-a000-000000000003",
            "name": "Send Booking Email",
            "credentials": {
                "gmailOAuth2": {
                    "id": "RmqsXSB26IzgIMJg",
                    "name": "Gmail account"
                }
            }
        },
        {
            "parameters": {
                "path": "booking-availability",
                "httpMethod": "POST",
                "responseMode": "responseNode",
                "options": {}
            },
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2.1,
            "position": [0, 400],
            "id": "a1b2c3d4-0004-4000-a000-000000000004",
            "name": "Get Availability",
            "webhookId": "a1b2c3d4-0004-4000-a000-000000000004"
        },
        {
            "parameters": {
                "jsCode": prepare_scrape_code
            },
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [220, 400],
            "id": "b1b2c3d4-0003-4000-a000-000000000003",
            "name": "Prepare Scrape"
        },
        {
            "parameters": {
                "conditions": {
                    "options": {
                        "caseSensitive": True,
                        "leftValue": "",
                        "typeValidation": "strict"
                    },
                    "conditions": [
                        {
                            "id": "has-scrape-url",
                            "leftValue": "={{ $json.url }}",
                            "rightValue": "",
                            "operator": {
                                "type": "string",
                                "operation": "notEquals"
                            }
                        }
                    ],
                    "combinator": "and"
                },
                "options": {}
            },
            "type": "n8n-nodes-base.if",
            "typeVersion": 2.2,
            "position": [440, 400],
            "id": "b1b2c3d4-0010-4000-a000-000000000010",
            "name": "Has Scrape URL?"
        },
        {
            "parameters": {
                "url": "={{ $json.url }}",
                "sendHeaders": True,
                "headerParameters": {
                    "parameters": [
                        {"name": "Accept", "value": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"},
                        {"name": "Accept-Language", "value": "en-US,en;q=0.9"},
                        {"name": "Cache-Control", "value": "max-age=0"},
                        {"name": "Connection", "value": "keep-alive"},
                        {"name": "Upgrade-Insecure-Requests", "value": "1"},
                        {"name": "User-Agent", "value": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"}
                    ]
                },
                "options": {}
            },
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.3,
            "position": [660, 340],
            "id": "b1b2c3d4-0004-4000-a000-000000000004",
            "name": "Scrape knetk.io",
            "continueOnFail": True
        },
        {
            "parameters": {
                "jsCode": parse_slots_code
            },
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [880, 400],
            "id": "b1b2c3d4-0005-4000-a000-000000000005",
            "name": "Parse & Format Slots"
        },
        {
            "parameters": {
                "respondWith": "firstIncomingItem",
                "options": {}
            },
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1.1,
            "position": [1100, 400],
            "id": "a1b2c3d4-0006-4000-a000-000000000006",
            "name": "Return Slots"
        }
    ],
    "connections": {
        "Booking Submit": {
            "main": [[
                {"node": "Respond Success", "type": "main", "index": 0},
                {"node": "Format Booking Email", "type": "main", "index": 0}
            ]]
        },
        "Format Booking Email": {
            "main": [[
                {"node": "Send Booking Email", "type": "main", "index": 0}
            ]]
        },
        "Get Availability": {
            "main": [[
                {"node": "Prepare Scrape", "type": "main", "index": 0}
            ]]
        },
        "Prepare Scrape": {
            "main": [[
                {"node": "Has Scrape URL?", "type": "main", "index": 0}
            ]]
        },
        "Has Scrape URL?": {
            "main": [
                [{"node": "Scrape knetk.io", "type": "main", "index": 0}],
                [{"node": "Parse & Format Slots", "type": "main", "index": 0}]
            ]
        },
        "Scrape knetk.io": {
            "main": [[
                {"node": "Parse & Format Slots", "type": "main", "index": 0}
            ]]
        },
        "Parse & Format Slots": {
            "main": [[
                {"node": "Return Slots", "type": "main", "index": 0}
            ]]
        }
    },
    "settings": {
        "executionOrder": "v1"
    }
}

with open('/tmp/booking_workflow.json', 'w') as f:
    json.dump(workflow, f)

print(f"Written. Nodes: {len(workflow['nodes'])}")
for n in workflow['nodes']:
    print(f"  - {n['name']} ({n['type'].split('.')[-1]})")
