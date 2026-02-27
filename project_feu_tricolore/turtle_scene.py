import turtle

# CONFIGURATION DE LA FENÊTRE
screen = turtle.Screen()
screen.title("Carrefour Routier Moderne")
screen.setup(width=1.0, height=1.0)
screen.bgcolor("#044F04")  # Vert prairie
screen.tracer(0)
screen_width = screen.window_width()
screen_hight = screen.window_height()

pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)
pen.penup()

def draw_rectangle(x, y, width, height, color, outline_color=None):
    pen.goto(x, y)
    pen.setheading(0)
    pen.fillcolor(color)
    if outline_color:
        pen.pencolor(outline_color)
        pen.pensize(2)
        pen.pendown()
    pen.begin_fill()
    for _ in range(2):
        pen.forward(width)
        pen.right(90)
        pen.forward(height)
        pen.right(90)
    pen.end_fill()
    pen.penup()

def draw_dashed_line(x1, y1, x2, y2, color="white", dash_length=20, gap=15):
    pen.goto(x1, y1)
    pen.setheading(pen.towards(x2, y2))
    pen.pencolor(color)
    pen.pensize(3)
    distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    traveled = 0
    while traveled < distance:
        pen.pendown()
        pen.forward(min(dash_length, distance - traveled))
        traveled += dash_length
        pen.penup()
        pen.forward(min(gap, distance - traveled))
        traveled += gap
    pen.penup()

def draw_roads():
    road_color = "#404040"
    sidewalk_color = "#A9A9A9"
    # Trottoirs
    draw_rectangle(-screen_width // 2, 70, screen_width, 140, sidewalk_color)
    draw_rectangle(-70, screen_hight // 2, 140, screen_hight, sidewalk_color)
    # Routes
    draw_rectangle(-screen_width // 2, 60, screen_width, 120, road_color)
    draw_rectangle(-60, screen_hight // 2, 120, screen_hight, road_color)
    # Intersection
    draw_rectangle(-60, 60, 120, 120, road_color)

def draw_road_markings():
    draw_dashed_line(-screen_width // 2, 0, -70, 0)
    draw_dashed_line(70, 0, screen_width // 2, 0)
    draw_dashed_line(0, screen_hight // 2, 0, 70)
    draw_dashed_line(0, -70, 0, -screen_hight // 2)

def draw_crosswalks():
    stripe_color = "white"
    stripe_width = 8
    stripe_height = 50
    gap = 12
    for i in range(-50, 51, gap + stripe_width):
        draw_rectangle(i, 120, stripe_width, stripe_height, stripe_color)
        draw_rectangle(i, -70, stripe_width, stripe_height, stripe_color)
        draw_rectangle(70, i, stripe_height, stripe_width, stripe_color)
        draw_rectangle(-120, i, stripe_height, stripe_width, stripe_color)

def setup_scene():
    pen.clear()
    draw_roads()
    draw_crosswalks()
    draw_road_markings()
    screen.update()