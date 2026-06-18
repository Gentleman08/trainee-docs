from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

BG = RGBColor(0x0F, 0x17, 0x2A)
ACCENT = RGBColor(0x3B, 0x82, 0xF6)
ACCENT2 = RGBColor(0x8B, 0x5C, 0xF6)
CYAN = RGBColor(0x06, 0xB6, 0xD4)
WHITE = RGBColor(0xF1, 0xF5, 0xF9)
GRAY = RGBColor(0x94, 0xA3, 0xB8)
DARK2 = RGBColor(0x1E, 0x29, 0x3B)
W, H = Inches(13.333), Inches(7.5)

prs = Presentation()
prs.slide_width = W
prs.slide_height = H

def bg(slide):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = BG

def box(slide, l, t, w, h, fill_color=DARK2, radius=None):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(l), Emu(t), Emu(w), Emu(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill_color
    s.line.fill.background()
    return s

def txt(slide, l, t, w, h, text, sz=18, color=WHITE, bold=False, align=PP_ALIGN.LEFT, font_name='Calibri'):
    txBox = slide.shapes.add_textbox(Emu(l), Emu(t), Emu(w), Emu(h))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(sz)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = align
    return txBox

def bullets(slide, l, t, w, h, items, sz=16, color=GRAY, bcolor=ACCENT):
    txBox = slide.shapes.add_textbox(Emu(l), Emu(t), Emu(w), Emu(h))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(6)
        # Arrow prefix
        run1 = p.add_run()
        run1.text = "→  "
        run1.font.size = Pt(sz)
        run1.font.color.rgb = bcolor
        run1.font.bold = True
        run1.font.name = 'Calibri'
        # Bold part
        if " — " in item:
            parts = item.split(" — ", 1)
            run2 = p.add_run()
            run2.text = parts[0]
            run2.font.size = Pt(sz)
            run2.font.color.rgb = WHITE
            run2.font.bold = True
            run2.font.name = 'Calibri'
            run3 = p.add_run()
            run3.text = " — " + parts[1]
            run3.font.size = Pt(sz)
            run3.font.color.rgb = color
            run3.font.name = 'Calibri'
        else:
            run2 = p.add_run()
            run2.text = item
            run2.font.size = Pt(sz)
            run2.font.color.rgb = color
            run2.font.name = 'Calibri'

def section_label(slide, text):
    txt(slide, 914400, 457200, 3048000, 365760, text, sz=13, color=ACCENT, bold=True)

def slide_title(slide, t1, t2=""):
    full = t1 + t2 if t2 else t1
    txBox = slide.shapes.add_textbox(Emu(914400), Emu(822960), Emu(10972800), Emu(731520))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    r1 = p.add_run()
    r1.text = t1
    r1.font.size = Pt(36)
    r1.font.color.rgb = WHITE
    r1.font.bold = True
    r1.font.name = 'Calibri'
    if t2:
        r2 = p.add_run()
        r2.text = t2
        r2.font.size = Pt(36)
        r2.font.color.rgb = ACCENT
        r2.font.bold = True
        r2.font.name = 'Calibri'

def card(slide, l, t, w, h, title, body_items, icon="", title_color=WHITE):
    box(slide, l, t, w, h)
    y = t + 182880
    if icon:
        txt(slide, l + 182880, t + 91440, 457200, 365760, icon, sz=28)
        y = t + 457200
    txt(slide, l + 182880, y, w - 365760, 365760, title, sz=17, color=title_color, bold=True)
    bullets(slide, l + 182880, y + 365760, w - 365760, h - (y - t) - 548640, body_items, sz=13, color=GRAY)

# ============== SLIDES ==============

# 1 - Title
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
txt(s, 914400, 457200, 10972800, 365760, "☁️  CLOUD ENGINEERING", sz=14, color=CYAN, bold=True, align=PP_ALIGN.CENTER)
txt(s, 914400, 2286000, 10972800, 1097280, "Azure Networking", sz=54, color=ACCENT, bold=True, align=PP_ALIGN.CENTER)
txt(s, 914400, 3474720, 10972800, 548640, "Core Services  •  Architecture Patterns  •  Security", sz=22, color=GRAY, align=PP_ALIGN.CENTER)
txt(s, 914400, 5486400, 10972800, 365760, "Professional Reference Deck", sz=14, color=GRAY, align=PP_ALIGN.CENTER)

# 2 - Agenda
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
section_label(s, "OVERVIEW")
slide_title(s, "What We'll ", "Cover")
bullets(s, 914400, 1828800, 10972800, 4572000, [
    "Virtual Networks (VNet) — Foundation of Azure networking",
    "Subnets & NSGs — Segmentation and traffic filtering",
    "Load Balancing — L4 Load Balancer, L7 App Gateway, Front Door",
    "DNS & Traffic Manager — Name resolution and global routing",
    "Hybrid Connectivity — VPN Gateway & ExpressRoute",
    "Security Services — Firewall, Bastion, Private Link, DDoS",
    "Architecture Patterns — Hub-Spoke, Zero Trust",
], sz=18)

# 3 - VNet
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
section_label(s, "SECTION 01")
slide_title(s, "Virtual Network ", "(VNet)")
card(s, 914400, 1828800, 5029200, 4114800, "What Is a VNet?", [
    "Isolated private network in Azure",
    "Address space via CIDR (e.g. 10.0.0.0/16)",
    "Scoped to a single Azure region",
    "Segmented into subnets",
    "Free — no cost for VNet itself",
], icon="🌐")
card(s, 6400800, 1828800, 5486400, 4114800, "Key Properties", [
    "All Azure resources live inside a VNet",
    "Cross-VNet via Peering or VPN Gateway",
    "Supports UDR (User Defined Routes)",
    "Built-in DDoS Basic protection",
    "DNS: Azure-provided or custom DNS",
], icon="⚡")

# 4 - Subnets & NSGs
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
section_label(s, "SECTION 02")
slide_title(s, "Subnets & ", "NSGs")
card(s, 914400, 1828800, 5029200, 4114800, "Subnets", [
    "Subdivisions of VNet address space",
    "Azure reserves 5 IPs per subnet",
    "Resources in same VNet talk freely",
    "Dedicated: GatewaySubnet, AzureFirewallSubnet",
    "Min size /29, recommended /24 or larger",
], icon="📦")
card(s, 6400800, 1828800, 5486400, 4114800, "Network Security Groups", [
    "Stateful L3/L4 firewall rules",
    "Filter by src/dst IP, port, protocol",
    "Priority: 100–4096 (lower = first)",
    "Default: allow VNet↔VNet, deny internet in",
    "Attach to subnet or NIC level",
], icon="🛡️")

# 5 - Load Balancing
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
section_label(s, "SECTION 03")
slide_title(s, "Load Balancing ", "Services")
card(s, 457200, 1828800, 3657600, 4114800, "Azure Load Balancer", [
    "Layer 4 (TCP/UDP)",
    "Regional scope",
    "Millions of flows/sec",
    "Public or Internal SKU",
    "Health probes for backends",
], icon="⚖️")
card(s, 4389120, 1828800, 3657600, 4114800, "Application Gateway", [
    "Layer 7 (HTTP/HTTPS)",
    "URL-based routing",
    "SSL offload & WAF",
    "Cookie-based affinity",
    "Autoscaling v2 SKU",
], icon="🔒")
card(s, 8321040, 1828800, 3657600, 4114800, "Azure Front Door", [
    "Global Layer 7",
    "CDN + LB + WAF combined",
    "Anycast acceleration",
    "Instant global failover",
    "Custom domain + managed certs",
], icon="🌍")

# 6 - LB Decision Table
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
section_label(s, "SECTION 03 — DECISION GUIDE")
slide_title(s, "Which ", "Load Balancer?")
rows = [
    ["Feature", "Load Balancer", "App Gateway", "Front Door", "Traffic Mgr"],
    ["Layer", "L4 TCP/UDP", "L7 HTTP/S", "L7 HTTP/S", "DNS-based"],
    ["Scope", "Regional", "Regional", "Global", "Global"],
    ["WAF", "✗", "✓", "✓", "✗"],
    ["SSL Offload", "✗", "✓", "✓", "✗"],
    ["URL Routing", "✗", "✓", "✓", "✗"],
    ["Best For", "VM fleet", "Web in region", "Global web", "DNS failover"],
]
col_w = 2194560
for ri, row in enumerate(rows):
    y = 1920240 + ri * 548640
    for ci, cell in enumerate(row):
        x = 914400 + ci * col_w
        c = WHITE if ri == 0 else (GRAY if ci > 0 else WHITE)
        b = ri == 0
        bg_c = RGBColor(0x16, 0x24, 0x3E) if ri == 0 else (DARK2 if ri % 2 == 0 else BG)
        box(s, x, y, col_w - 45720, 502920, bg_c)
        txt(s, x + 91440, y + 91440, col_w - 228600, 365760, cell, sz=13, color=c, bold=b)

# 7 - VNet Peering
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
section_label(s, "SECTION 04")
slide_title(s, "VNet ", "Peering")
card(s, 914400, 1828800, 5029200, 4114800, "How It Works", [
    "Connects two VNets via Microsoft backbone",
    "Private, low-latency, high-bandwidth",
    "Regional peering — free data transfer",
    "Global peering — cross-region, egress cost",
    "Non-transitive: A↔B + B↔C ≠ A↔C",
    "No overlapping CIDR ranges allowed",
], icon="🔗")
card(s, 6400800, 1828800, 5486400, 4114800, "Common Pattern", [
    "Hub VNet: shared services (FW, VPN, DNS)",
    "Spoke VNets: workload-specific",
    "Each Spoke peers with Hub only",
    "Use UDR to force traffic through Hub FW",
    "Scales to 500 peerings per VNet",
], icon="🏗️")

# 8 - DNS
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
section_label(s, "SECTION 05")
slide_title(s, "Azure ", "DNS")
card(s, 914400, 1828800, 5029200, 4114800, "Public DNS Zones", [
    "Host domain records on Azure nameservers",
    "A, CNAME, MX, TXT, SRV records",
    "100% availability SLA with anycast",
    "Alias records for Azure resources",
    "RBAC-controlled DNS management",
], icon="📛")
card(s, 6400800, 1828800, 5486400, 4114800, "Private DNS Zones", [
    "Internal name resolution inside VNets",
    "No custom DNS server needed",
    "Auto-registration of VM hostnames",
    "Link to multiple VNets",
    "Critical for Private Endpoints",
], icon="🔐")

# 9 - Hybrid (VPN + ER)
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
section_label(s, "SECTION 06")
slide_title(s, "Hybrid ", "Connectivity")
card(s, 914400, 1828800, 5029200, 4114800, "VPN Gateway", [
    "IPsec tunnel over public internet",
    "Site-to-Site: DC ↔ Azure VNet",
    "Point-to-Site: laptop ↔ Azure VNet",
    "Up to 10 Gbps (VpnGw5 SKU)",
    "Active-Active for high availability",
    "Requires GatewaySubnet (/27 min)",
], icon="🔒")
card(s, 6400800, 1828800, 5486400, 4114800, "ExpressRoute", [
    "Private dedicated fiber — not over internet",
    "50 Mbps – 100 Gbps speeds",
    "Predictable latency, high reliability",
    "BGP dynamic routing",
    "99.95% SLA (99.99% redundant)",
    "Use for mission-critical production",
], icon="⚡")

# 10 - Security
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
section_label(s, "SECTION 07")
slide_title(s, "Network ", "Security")
card(s, 457200, 1828800, 2743200, 4114800, "Azure Firewall", [
    "Managed L3–L7 firewall",
    "FQDN filtering",
    "Threat intelligence feed",
    "Centralized in Hub VNet",
], icon="🔥")
card(s, 3383280, 1828800, 2743200, 4114800, "Azure Bastion", [
    "Managed jump host",
    "RDP/SSH via browser",
    "No public IPs on VMs",
    "Zero-attack surface",
], icon="🏰")
card(s, 6309360, 1828800, 2743200, 4114800, "Private Link", [
    "Private IP for PaaS services",
    "SQL, Storage, Key Vault",
    "Traffic on MS backbone",
    "Disable public access",
], icon="🔗")
card(s, 9235440, 1828800, 2743200, 4114800, "DDoS Protection", [
    "Always-on monitoring",
    "Basic: free, auto-enabled",
    "Standard: adaptive tuning",
    "Cost protection guarantee",
], icon="🛡️")

# 11 - Private Endpoints detail
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
section_label(s, "SECTION 07 — DEEP DIVE")
slide_title(s, "Private Endpoints vs ", "Service Endpoints")
rows2 = [
    ["Feature", "Service Endpoint", "Private Endpoint"],
    ["Mechanism", "Optimized route to PaaS", "Private IP (NIC) in VNet"],
    ["PaaS Public IP", "Still exists (restricted)", "Can disable completely"],
    ["On-Prem Access", "✗  VNet traffic only", "✓  Via VPN / ExpressRoute"],
    ["DNS Change", "No", "Yes — Private DNS Zone"],
    ["Cost", "Free", "~$7.30/mo + data"],
    ["Best For", "Dev/test, quick wins", "Production — full isolation"],
]
col_w2 = 3383280
for ri, row in enumerate(rows2):
    y = 1920240 + ri * 548640
    for ci, cell in enumerate(row):
        x = 914400 + ci * col_w2
        c = WHITE if ri == 0 else (GRAY if ci > 0 else WHITE)
        b = ri == 0
        bg_c = RGBColor(0x16, 0x24, 0x3E) if ri == 0 else (DARK2 if ri % 2 == 0 else BG)
        box(s, x, y, col_w2 - 45720, 502920, bg_c)
        txt(s, x + 91440, y + 91440, col_w2 - 228600, 365760, cell, sz=14, color=c, bold=b)

# 12 - Hub-Spoke
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
section_label(s, "SECTION 08")
slide_title(s, "Hub-Spoke ", "Architecture")
card(s, 914400, 1828800, 5029200, 4114800, "Hub VNet — Shared Services", [
    "Azure Firewall — centralized traffic inspection",
    "VPN/ExpressRoute Gateway — hybrid connectivity",
    "Bastion Host — secure admin access",
    "DNS servers — centralized resolution",
    "All spoke traffic routes through hub",
], icon="🏛️")
card(s, 6400800, 1828800, 5486400, 4114800, "Spoke VNets — Workloads", [
    "Spoke 1 (Prod) — Web + API + databases",
    "Spoke 2 (Dev) — Test & staging environments",
    "Spoke 3 (DMZ) — Public-facing services",
    "Spokes isolated from each other by default",
    "UDRs force traffic through Hub Firewall",
], icon="🔄")

# 13 - Key Takeaways
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
section_label(s, "SUMMARY")
slide_title(s, "Key ", "Takeaways")
bullets(s, 914400, 1828800, 10972800, 4572000, [
    "VNet is your foundation — design address spaces before deploying",
    "NSGs are first defense — apply at subnet level with deny-all baseline",
    "Use Private Endpoints — eliminate public exposure for PaaS services",
    "Pick the right LB — L4 for VMs, App GW for web, Front Door for global",
    "Hub-Spoke for enterprise — centralize firewall and gateway in hub",
    "ExpressRoute for production — VPN for dev, ER for mission-critical",
    "Network Watcher is your debugger — IP Flow Verify & Connection Troubleshoot",
], sz=18)

# 14 - Thank You
s = prs.slides.add_slide(prs.slide_layouts[6])
bg(s)
txt(s, 914400, 2286000, 10972800, 1097280, "Thank You", sz=54, color=ACCENT, bold=True, align=PP_ALIGN.CENTER)
txt(s, 914400, 3474720, 10972800, 548640, "Azure Networking — Core Services, Architecture & Security", sz=22, color=GRAY, align=PP_ALIGN.CENTER)
txt(s, 914400, 4572000, 10972800, 365760, "Questions?  Let's discuss.", sz=16, color=GRAY, align=PP_ALIGN.CENTER)

# Save
out = os.path.join(os.path.dirname(__file__), "Azure_Networking.pptx")
prs.save(out)
print(f"✅ Saved: {out}")
