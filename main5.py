import flet as ft
import datetime

# --- Data Models & State ---

class Device:
    def __init__(self, dev_id, name, dev_type, state, details_desc, bg_color):
        self.id = dev_id
        self.name = name
        self.type = dev_type
        self.state = state  # Can be "ON", "OFF", "LOCKED", "UNLOCKED", or a number/float
        self.details_desc = details_desc
        self.bg_color = bg_color

class AppState:
    def __init__(self):
        self.devices = {
            "light1": Device("light1", "Living Room Light", "light", "OFF", "Tap to switch the light.", "orange100"),
            "door1": Device("door1", "Front Door", "lock", "LOCKED", "Tap to lock / unlock the door.", "indigo100"),
            "thermostat1": Device("thermostat1", "Thermostat", "thermostat", 22.0, "Use slider to change temperature.", "deepOrange50"),
            "fan1": Device("fan1", "Ceiling Fan", "fan", 0, "0 = OFF, 3 = MAX", "cyan100"),
        }
        self.logs = [
            {"time": "08:12:32", "device": "light1", "action": "Turn ON", "user": "User"},
            {"time": "08:13:23", "device": "light1", "action": "Turn OFF", "user": "User"},
            {"time": "08:13:26", "device": "light1", "action": "Turn ON", "user": "User"},
        ]

    def get_device(self, dev_id):
        return self.devices.get(dev_id)

    def toggle_device(self, dev_id):
        dev = self.devices.get(dev_id)
        if dev:
            if dev.type == "light":
                dev.state = "ON" if dev.state == "OFF" else "OFF"
            elif dev.type == "lock":
                dev.state = "LOCKED" if dev.state == "UNLOCKED" else "UNLOCKED"
            self.log_action(dev_id, f"Set to {dev.state}")

    def set_device_value(self, dev_id, value):
        dev = self.devices.get(dev_id)
        if dev:
            dev.state = value
            # self.log_action(dev_id, f"Set to {value}") # Optional: log slider changes

    def log_action(self, dev_id, action):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.logs.insert(0, {"time": now, "device": dev_id, "action": action, "user": "User"})


app_state = AppState()

# --- Views ---

def main(page: ft.Page):
    page.title = "Smart Home Controller + Simulator"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    page.window_width = 1100
    page.window_height = 900
    page.bgcolor = "grey50" # Light background for the whole app
    page.fonts = {
        "Roboto": "https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap"
    }
    page.theme = ft.Theme(font_family="Roboto")

    def route_change(route):
        page.views.clear()
        
        # Common Header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Row([
                        ft.Icon("home", size=30, color="blue600"),
                        ft.Text("Smart Home", size=24, weight=ft.FontWeight.BOLD, color="blueGrey900"),
                    ]),
                    ft.Row(
                        [
                            ft.TextButton("Overview", on_click=lambda _: page.go("/"), style=ft.ButtonStyle(color="blue600")),
                            ft.TextButton("Statistics", on_click=lambda _: page.go("/stats"), style=ft.ButtonStyle(color="blue600")),
                        ]
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.padding.only(bottom=20)
        )

        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    [
                        header,
                        create_overview_view(page)
                    ],
                    padding=30,
                    bgcolor="grey50",
                    scroll=ft.ScrollMode.AUTO
                )
            )
        elif page.route == "/stats":
            page.views.append(
                ft.View(
                    "/stats",
                    [
                        header,
                        create_statistics_view(page)
                    ],
                    padding=30,
                    bgcolor="grey50",
                    scroll=ft.ScrollMode.AUTO
                )
            )
        elif page.route.startswith("/details/"):
            dev_id = page.route.split("/")[-1]
            page.views.append(
                ft.View(
                    f"/details/{dev_id}",
                    [
                        header,
                        create_details_view(page, dev_id)
                    ],
                    padding=30,
                    bgcolor="grey50",
                    scroll=ft.ScrollMode.AUTO
                )
            )
        
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

def create_overview_view(page):
    
    # Dictionaries to store mutable controls
    # Key: dev_id, Value: Control
    status_texts = {}
    action_buttons = {}
    value_labels = {}
    slider_controls = {}

    def go_details(e):
        dev_id = e.control.data
        page.go(f"/details/{dev_id}")

    def toggle_click(e):
        dev_id = e.control.data
        app_state.toggle_device(dev_id)
        dev = app_state.get_device(dev_id)
        
        # Update UI
        if dev_id in status_texts:
            status_text = f"Status: {dev.state}"
            if dev.type == "lock":
                status_text = f"Door: {dev.state}"
            status_texts[dev_id].value = status_text
            
        if dev_id in action_buttons:
            btn_text = "Turn ON" if dev.state == "OFF" else "Turn OFF"
            if dev.type == "lock":
                btn_text = "Unlock" if dev.state == "LOCKED" else "Lock"
            action_buttons[dev_id].text = btn_text
            
        page.update()

    def slider_change(e):
        dev_id = e.control.data
        val = e.control.value
        app_state.set_device_value(dev_id, val)
        dev = app_state.get_device(dev_id)

        if dev_id in value_labels:
            val_text = f"Set point: {dev.state} °C" if dev.type == "thermostat" else f"Fan speed: {int(dev.state)}"
            value_labels[dev_id].value = val_text
            
        page.update()

    # Helper to build On/Off Card
    def build_on_off_card(dev_id, icon, icon_color):
        dev = app_state.get_device(dev_id)
        btn_text = "Turn ON" if dev.state == "OFF" else "Turn OFF"
        if dev.type == "lock":
            btn_text = "Unlock" if dev.state == "LOCKED" else "Lock"
        
        # Status text
        status_str = f"Status: {dev.state}"
        if dev.type == "lock":
            status_str = f"Door: {dev.state}"
        
        # Create controls
        txt_status = ft.Text(status_str, size=12, weight=ft.FontWeight.W_500)
        btn_action = ft.ElevatedButton(
            btn_text, 
            data=dev_id, 
            on_click=toggle_click, 
            bgcolor="white", 
            color="blueGrey800",
            elevation=2
        )

        # Store refs
        status_texts[dev_id] = txt_status
        action_buttons[dev_id] = btn_action

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row([
                        ft.Container(content=ft.Icon(icon, color=icon_color, size=24), padding=5, bgcolor="white", border_radius=50),
                        ft.Text(dev.name, weight=ft.FontWeight.BOLD, size=16, color="blueGrey900")
                    ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Container(height=5),
                    txt_status,
                    ft.Text(dev.details_desc, size=12, color="blueGrey600"),
                    ft.Container(height=10),
                    ft.Row(
                        [
                            ft.TextButton("Details", data=dev_id, on_click=go_details, style=ft.ButtonStyle(color="blue600")),
                            btn_action
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                ],
                spacing=0
            ),
            bgcolor=dev.bg_color,
            padding=20,
            border_radius=15,
            width=320,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color="#1A000000",
                offset=ft.Offset(0, 4),
            )
        )

    # Helper to build Slider Card
    def build_slider_card(dev_id, icon, icon_color, min_val, max_val, divisions, label_fmt):
        dev = app_state.get_device(dev_id)
        
        # Dynamic label for value
        val_text = f"Set point: {dev.state} °C" if dev.type == "thermostat" else f"Fan speed: {int(dev.state)}"
        
        txt_val = ft.Text(val_text, size=12, weight=ft.FontWeight.W_500)
        value_labels[dev_id] = txt_val

        slider = ft.Slider(
            min=min_val, 
            max=max_val, 
            divisions=divisions, 
            value=dev.state, 
            label=label_fmt, 
            data=dev_id,
            on_change=slider_change,
            active_color="blue600"
        )
        slider_controls[dev_id] = slider

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row([
                        ft.Container(content=ft.Icon(icon, color=icon_color, size=24), padding=5, bgcolor="white", border_radius=50),
                        ft.Text(dev.name, weight=ft.FontWeight.BOLD, size=16, color="blueGrey900")
                    ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Container(height=5),
                    txt_val,
                    ft.Text(dev.details_desc, size=12, color="blueGrey600"),
                    slider,
                    ft.Row(
                        [
                            ft.Container(), # Spacer
                            ft.TextButton("Details", data=dev_id, on_click=go_details, style=ft.ButtonStyle(color="blue600")),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                ],
                spacing=0
            ),
            bgcolor=dev.bg_color,
            padding=20,
            border_radius=15,
            width=320,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color="#1A000000",
                offset=ft.Offset(0, 4),
            )
        )

    # Helper to build System Status Card
    def build_system_status_card():
        now = datetime.datetime.now().strftime("%H:%M")
        date_str = datetime.datetime.now().strftime("%A, %d %B")
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("System Status", weight=ft.FontWeight.BOLD, size=18, color="blueGrey800"),
                    ft.Container(height=10),
                    ft.Row([
                        ft.Icon("access_time", size=40, color="blue600"),
                        ft.Column([
                            ft.Text(now, size=28, weight=ft.FontWeight.BOLD, color="blueGrey900"),
                            ft.Text(date_str, size=14, color="blueGrey600"),
                        ], spacing=0)
                    ]),
                    ft.Container(height=20),
                    ft.Row([
                        ft.Icon("cloud", size=30, color="blue400"),
                        ft.Text("Kuopio: -2°C, Snowy", size=16, weight=ft.FontWeight.W_500, color="blueGrey800"),
                    ]),
                    ft.Container(height=10),
                    ft.Row([
                        ft.Icon("wifi", size=30, color="green500"),
                        ft.Text("Network Online", size=16, weight=ft.FontWeight.W_500, color="blueGrey800"),
                    ]),
                    ft.Container(height=10),
                    ft.Row([
                        ft.Icon("security", size=30, color="green500"),
                        ft.Text("System Armed", size=16, weight=ft.FontWeight.W_500, color="blueGrey800"),
                    ]),
                ],
                spacing=5
            ),
            bgcolor="white",
            padding=20,
            border_radius=15,
            width=300,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color="#1A000000",
                offset=ft.Offset(0, 4),
            )
        )

    # Helper to build Scenes Card
    def build_scenes_card():
        def scene_click(e):
            scene_name = e.control.text
            if scene_name == "Home":
                app_state.toggle_device("light1") # Ensure ON? Simple toggle for now or set specific state
                # Better: Set specific states
                dev_light = app_state.get_device("light1")
                dev_light.state = "ON"
                dev_door = app_state.get_device("door1")
                dev_door.state = "UNLOCKED"
                app_state.log_action("SCENE", "Activated Home Scene")
                
            elif scene_name == "Away":
                dev_light = app_state.get_device("light1")
                dev_light.state = "OFF"
                dev_door = app_state.get_device("door1")
                dev_door.state = "LOCKED"
                app_state.log_action("SCENE", "Activated Away Scene")

            elif scene_name == "Night":
                dev_light = app_state.get_device("light1")
                dev_light.state = "OFF"
                dev_door = app_state.get_device("door1")
                dev_door.state = "LOCKED"
                dev_fan = app_state.get_device("fan1")
                dev_fan.state = 1
                app_state.log_action("SCENE", "Activated Night Scene")
                
            elif scene_name == "Party":
                dev_light = app_state.get_device("light1")
                dev_light.state = "ON"
                dev_door = app_state.get_device("door1")
                dev_door.state = "UNLOCKED"
                dev_fan = app_state.get_device("fan1")
                dev_fan.state = 2
                app_state.log_action("SCENE", "Activated Party Scene")

            # Force UI update for all devices
            # We need to update the specific controls. 
            # Since we don't have easy access to them here without refetching or storing them globally,
            # we can trigger a full page update or call the update logic if we refactor.
            # For now, let's just update the page and rely on the fact that we might need to 
            # manually update the text/buttons if they are not reactive.
            # Wait, the controls in `create_overview_view` are created once. 
            # We need to update `status_texts` and `action_buttons`.
            
            # To do this properly, we should iterate over the `status_texts` and update them.
            # But `status_texts` is local to `create_overview_view`.
            # We can access them if we define `scene_click` inside `create_overview_view` (which it is).
            
            for dev_id, txt in status_texts.items():
                dev = app_state.get_device(dev_id)
                status_str = f"Status: {dev.state}"
                if dev.type == "lock":
                    status_str = f"Door: {dev.state}"
                txt.value = status_str
                
            for dev_id, btn in action_buttons.items():
                dev = app_state.get_device(dev_id)
                btn_text = "Turn ON" if dev.state == "OFF" else "Turn OFF"
                if dev.type == "lock":
                    btn_text = "Unlock" if dev.state == "LOCKED" else "Lock"
                btn.text = btn_text

            for dev_id, slider in slider_controls.items():
                dev = app_state.get_device(dev_id)
                slider.value = dev.state
            
            for dev_id, txt in value_labels.items():
                 dev = app_state.get_device(dev_id)
                 val_text = f"Set point: {dev.state} °C" if dev.type == "thermostat" else f"Fan speed: {int(dev.state)}"
                 txt.value = val_text

            page.update()
            
            # Show feedback
            # Try page.open if available, else fallback
            try:
                page.open(ft.SnackBar(ft.Text(f"Activated {scene_name} Scene")))
            except:
                page.snack_bar = ft.SnackBar(ft.Text(f"Activated {scene_name} Scene"))
                page.snack_bar.open = True
                page.update()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Quick Scenes", weight=ft.FontWeight.BOLD, size=18, color="blueGrey800"),
                    ft.Container(height=10),
                    ft.Row([
                        ft.ElevatedButton("Home", icon="home", on_click=scene_click, bgcolor="blue50", color="blue800", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))),
                        ft.ElevatedButton("Away", icon="directions_walk", on_click=scene_click, bgcolor="blue50", color="blue800", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(height=10),
                    ft.Row([
                        ft.ElevatedButton("Night", icon="bedtime", on_click=scene_click, bgcolor="blue50", color="blue800", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))),
                        ft.ElevatedButton("Party", icon="music_note", on_click=scene_click, bgcolor="blue50", color="blue800", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ],
                spacing=5
            ),
            bgcolor="white",
            padding=20,
            border_radius=15,
            width=300,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color="#1A000000",
                offset=ft.Offset(0, 4),
            )
        )

    # Helper to build Camera Card
    def build_camera_card():
        # Camera definitions
        cameras = [
            {"name": "Front Door", "src": "/front_door.png"},
            {"name": "Back Door", "src": "/back_door.png"}
        ]
        
        # We need to store the current camera index. 
        current_cam = [0] # List to be mutable in closure

        # Initial Image
        cam = cameras[current_cam[0]]
        
        img_control = ft.Image(
            src=cam['src'],
            width=300,
            height=200,
            fit=ft.ImageFit.COVER,
            border_radius=10,
            gapless_playback=True
        )
        
        txt_cam_name = ft.Text(f"CAM 0{current_cam[0]+1} - {cam['name']}", color="white", size=12, weight=ft.FontWeight.BOLD)

        def next_camera(e):
            # Cycle camera
            current_cam[0] = (current_cam[0] + 1) % len(cameras)
            cam = cameras[current_cam[0]]
            
            # Update Image
            img_control.src = cam['src']
            
            # Update Label
            txt_cam_name.value = f"CAM 0{current_cam[0]+1} - {cam['name']}"
            
            page.update()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row([
                        ft.Text("Security Camera", weight=ft.FontWeight.BOLD, size=18, color="blueGrey800"),
                        ft.Container(content=ft.Text("LIVE", color="white", size=10, weight=ft.FontWeight.BOLD), bgcolor="red", padding=ft.padding.symmetric(horizontal=5, vertical=2), border_radius=5)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(height=10),
                    ft.Stack(
                        [
                            img_control,
                            ft.Container(
                                content=txt_cam_name,
                                padding=5,
                                bgcolor="#80000000",
                                border_radius=ft.border_radius.only(bottom_right=10, top_left=10),
                                alignment=ft.alignment.bottom_right,
                                bottom=0,
                                right=0
                            )
                        ]
                    ),
                    ft.Container(height=10),
                    ft.ElevatedButton("Switch Camera", icon="switch_camera", on_click=next_camera, bgcolor="blue50", color="blue800", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))),
                ],
                spacing=5
            ),
            bgcolor="white",
            padding=20,
            border_radius=15,
            width=300,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color="#1A000000",
                offset=ft.Offset(0, 4),
            )
        )

    return ft.Row(
        [
            # Left Column (Devices)
            ft.Column(
                [
                    ft.Text("On/Off devices", weight=ft.FontWeight.BOLD, size=18, color="blueGrey800"),
                    ft.Row(
                        [
                            build_on_off_card("light1", "lightbulb", "orange700"),
                            build_on_off_card("door1", "door_front_door", "indigo700"),
                        ],
                        wrap=True,
                        spacing=20,
                        run_spacing=20
                    ),
                    ft.Container(height=30),
                    ft.Text("Slider controlled devices", weight=ft.FontWeight.BOLD, size=18, color="blueGrey800"),
                    ft.Row(
                        [
                            build_slider_card("thermostat1", "thermostat", "deepOrange700", 10, 30, 20, "{value}°C"),
                            build_slider_card("fan1", "wind_power", "cyan700", 0, 3, 3, "{value}"),
                        ],
                        wrap=True,
                        spacing=20,
                        run_spacing=20
                    )
                ],
                expand=True,
            ),
            # Right Column (Widgets)
            ft.Column(
                [
                    build_camera_card(),
                    ft.Container(height=20),
                    build_system_status_card(),
                    ft.Container(height=20),
                    build_scenes_card(),
                ],
                alignment=ft.MainAxisAlignment.START,
            )
        ],
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=30
    )

def create_statistics_view(page):
    # Mock data for chart
    data_points = [
        ft.LineChartDataPoint(0, 3),
        ft.LineChartDataPoint(1, 2),
        ft.LineChartDataPoint(2, 5),
        ft.LineChartDataPoint(3, 3.5),
        ft.LineChartDataPoint(4, 4),
        ft.LineChartDataPoint(5, 3),
        ft.LineChartDataPoint(6, 4),
        ft.LineChartDataPoint(7, 3),
        ft.LineChartDataPoint(8, 4),
        ft.LineChartDataPoint(9, 3),
    ]

    chart = ft.LineChart(
        data_series=[
            ft.LineChartData(
                data_points=data_points,
                stroke_width=3,
                color="cyan600",
                curved=True,
                stroke_cap_round=True,
                below_line_bgcolor="#3300FFFF",
            )
        ],
        border=ft.border.all(1, "grey300"),
        left_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(
                    value=1, label=ft.Text("100W", size=10, weight=ft.FontWeight.BOLD, color="grey600")
                ),
                ft.ChartAxisLabel(
                    value=3, label=ft.Text("300W", size=10, weight=ft.FontWeight.BOLD, color="grey600")
                ),
                ft.ChartAxisLabel(
                    value=5, label=ft.Text("500W", size=10, weight=ft.FontWeight.BOLD, color="grey600")
                ),
            ],
            labels_size=40,
        ),
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(
                    value=0, label=ft.Text("00:00", size=10, weight=ft.FontWeight.BOLD, color="grey600")
                ),
                ft.ChartAxisLabel(
                    value=5, label=ft.Text("12:00", size=10, weight=ft.FontWeight.BOLD, color="grey600")
                ),
                ft.ChartAxisLabel(
                    value=9, label=ft.Text("24:00", size=10, weight=ft.FontWeight.BOLD, color="grey600")
                ),
            ],
            labels_size=32,
        ),
        tooltip_bgcolor="#CC263238",
        min_y=0,
        max_y=6,
        min_x=0,
        max_x=9,
        expand=True,
    )

    # Data Table
    rows = []
    for log in app_state.logs:
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(log["time"], color="blueGrey700")),
                    ft.DataCell(ft.Text(log["device"], weight=ft.FontWeight.W_500)),
                    ft.DataCell(ft.Text(log["action"])),
                    ft.DataCell(ft.Text(log["user"])),
                ]
            )
        )

    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Time", weight=ft.FontWeight.BOLD, color="blueGrey800")),
            ft.DataColumn(ft.Text("Device", weight=ft.FontWeight.BOLD, color="blueGrey800")),
            ft.DataColumn(ft.Text("Action", weight=ft.FontWeight.BOLD, color="blueGrey800")),
            ft.DataColumn(ft.Text("User", weight=ft.FontWeight.BOLD, color="blueGrey800")),
        ],
        rows=rows,
        border=ft.border.all(1, "grey200"),
        vertical_lines=ft.border.BorderSide(1, "grey100"),
        horizontal_lines=ft.border.BorderSide(1, "grey100"),
        heading_row_color="grey100",
    )

    return ft.Column(
        [
            ft.Text("Power consumption (simulated)", weight=ft.FontWeight.BOLD, size=18, color="blueGrey800"),
            ft.Container(
                content=chart,
                height=250,
                bgcolor="white",
                padding=20,
                border_radius=15,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color="#0D000000",
                    offset=ft.Offset(0, 4),
                )
            ),
            ft.Container(height=30),
            ft.Text("Action log", weight=ft.FontWeight.BOLD, size=18, color="blueGrey800"),
            ft.Container(
                content=data_table,
                bgcolor="white",
                border_radius=15,
                padding=10,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color="#0D000000",
                    offset=ft.Offset(0, 4),
                )
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

def create_details_view(page, dev_id):
    dev = app_state.get_device(dev_id)
    if not dev:
        return ft.Text("Device not found")

    # Filter logs for this device (mock logic, in real app we'd filter properly)
    device_logs = [l for l in app_state.logs if l["device"] == dev_id]

    log_items = []
    for log in device_logs:
        log_items.append(ft.Text(f"{log['time']} - {log['action']} ({log['user']})", color="blueGrey700"))

    return ft.Container(
        content=ft.Column(
            [
                ft.Row([
                    ft.Icon("info_outline", color="blue600", size=30),
                    ft.Text(f"{dev.name} details", size=24, weight=ft.FontWeight.BOLD, color="blueGrey900"),
                ]),
                ft.Container(height=10),
                ft.Text(f"ID: {dev.id}", color="blueGrey600"),
                ft.Text(f"Type: {dev.type}", color="blueGrey600"),
                ft.Text(f"State: {dev.state}", size=16, weight=ft.FontWeight.BOLD, color="blueGrey800"),
                ft.Divider(color="grey300"),
                ft.Text("Recent actions", size=18, weight=ft.FontWeight.BOLD, color="blueGrey800"),
                ft.Column(log_items),
                ft.Container(height=20),
                ft.ElevatedButton("Back to overview", on_click=lambda _: page.go("/"), bgcolor="blue600", color="white")
            ],
            spacing=10
        ),
        bgcolor="white",
        padding=30,
        border_radius=15,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color="#1A000000",
            offset=ft.Offset(0, 4),
        )
    )

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
