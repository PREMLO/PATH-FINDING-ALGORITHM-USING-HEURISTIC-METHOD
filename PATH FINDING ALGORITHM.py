import pygame
import heapq

# Function to calculate obstacle proximity
def calculate_obstacle_proximity(map, x, y, max_distance=5):
    obstacle_cost = 0
    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    for dx, dy in neighbors:
        for distance in range(1, max_distance + 1):
            new_x = x + dx * distance
            new_y = y + dy * distance
            if 0 <= new_x < len(map[0]) and 0 <= new_y < len(map):
                if map[new_y][new_x] == '1':
                    obstacle_cost += 1 / distance  # Closer obstacles have a higher cost
                    break  # Stop once we find an obstacle in a direction
    return obstacle_cost

# Original heuristic function
def heuristic_original(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Obstacle-aware heuristic function
def heuristic_obstacle_aware(a, b):
    distance = abs(a[0] - b[0]) + abs(a[1] - b[1])
    obstacle_proximity_a = calculate_obstacle_proximity(MAP, a[0], a[1])
    obstacle_proximity_b = calculate_obstacle_proximity(MAP, b[0], b[1])
    return distance + obstacle_proximity_a + 5 * obstacle_proximity_b

# A* algorithm implementation
def astar(map, start, end, heuristic):
    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # 4-directional movement

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == end:
            break

        for next in neighbors:
            new_x = current[0] + next[0]
            new_y = current[1] + next[1]
            if (0 <= new_x < len(map[0]) and 0 <= new_y < len(map)  # Check map bounds
                    and map[new_y][new_x] != '1'):  # Check if not a wall
                new_cost = cost_so_far[current] + 1
                if (new_x, new_y) not in cost_so_far or new_cost < cost_so_far[new_x, new_y]:
                    cost_so_far[new_x, new_y] = new_cost
                    priority = new_cost + heuristic(end, (new_x, new_y))
                    heapq.heappush(open_set, (priority, (new_x, new_y)))
                    came_from[new_x, new_y] = current

    return reconstruct_path(came_from, start, end)

# Function to reconstruct path
def reconstruct_path(came_from, start, end):
    path = []
    current = end
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse()  # Return from start to end
    return path

# Constants
TILESIZE = 64
WIDTH = TILESIZE * 16
HEIGHT = TILESIZE * 12
PLAYER_SPEED = 3 * TILESIZE

# Map definition
MAP = [
    "1111111111111111",
    "1..............1",
    "1...........P..1",
    "1..1111........1",
    "1..1..1........1",
    "1..1111........1",
    "1..............1",
    "1........11111.1",
    "1........1...1.1",
    "1........11111.1",
    "1..............1",
    "1111111111111111"
]

# Function to get grid position from mouse position
def get_grid_pos(mouse_pos):
    return mouse_pos[0] // TILESIZE, mouse_pos[1] // TILESIZE

# Player class definition
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.walk_buffer = 50
        self.pos = pygame.math.Vector2(x, y) * TILESIZE
        self.dirvec = pygame.math.Vector2(0, 0)
        self.last_pos = self.pos
        self.next_pos = self.pos
        
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.between_tiles = False
        
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(self.pos.x, self.pos.y))

    def update(self, dt, walls):
        self.get_keys()
        self.rect = self.image.get_rect(topleft=(self.pos.x, self.pos.y))
        
        if self.pos != self.next_pos:
            delta = self.next_pos - self.pos
            if delta.length() > (self.dirvec * PLAYER_SPEED * dt).length():
                self.pos += self.dirvec * PLAYER_SPEED * dt
            else:
                self.pos = self.next_pos
                self.dirvec = pygame.math.Vector2(0, 0)
                self.between_tiles = False
                    
        self.rect.topleft = self.pos
        if pygame.sprite.spritecollide(self, walls, False):
            self.pos = self.last_pos
            self.next_pos = self.last_pos
            self.dirvec = pygame.math.Vector2(0, 0)
            self.between_tiles = False
        self.rect.topleft = self.pos

    def get_keys(self):        
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        
        if now - self.last_update > self.walk_buffer:
            self.last_update = now
            
            new_dir_vec = pygame.math.Vector2(0, 0)
            if self.dirvec.y == 0:
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    new_dir_vec = pygame.math.Vector2(-1, 0)
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    new_dir_vec = pygame.math.Vector2(1, 0)
            if self.dirvec.x == 0:
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    new_dir_vec = pygame.math.Vector2(0, -1)
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    new_dir_vec = pygame.math.Vector2(0, 1)
                
            if new_dir_vec != pygame.math.Vector2(0, 0):
                self.dirvec = new_dir_vec
                self.between_tiles = True
                current_index = self.rect.centerx // TILESIZE, self.rect.centery // TILESIZE
                self.last_pos = pygame.math.Vector2(current_index) * TILESIZE
                self.next_pos = self.last_pos + self.dirvec * TILESIZE
                
# Obstacle class definition
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect(topleft=(x * TILESIZE, y * TILESIZE))

# Destination class definition
class Destination(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.image.fill((0, 255, 0))  # Green color for destination
        self.rect = self.image.get_rect(topleft=(x * TILESIZE, y * TILESIZE))

# Initialize Pygame
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
walls = pygame.sprite.Group()
path = []

# Create map with obstacles and player
for row, tiles in enumerate(MAP):
    for col, tile in enumerate(tiles):
        if tile == "1":
            obstacle = Obstacle(col, row)
            walls.add(obstacle)
            all_sprites.add(obstacle)
        elif tile == "P":
            player = Player(col, row)
            all_sprites.add(player)

# Main game loop
run = True
destination = None
while run:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        # Check for left mouse click to place player
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            grid_x, grid_y = get_grid_pos(mouse_pos)
            if MAP[grid_y][grid_x] != "1":
                player.pos = pygame.math.Vector2(grid_x, grid_y) * TILESIZE
                player.rect.topleft = player.pos
        # Check for right mouse click to update destination
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if destination is not None:  # Remove existing destination if present
                all_sprites.remove(destination)
            mouse_pos = pygame.mouse.get_pos()
            grid_x, grid_y = get_grid_pos(mouse_pos)
            if MAP[grid_y][grid_x] != "1":
                destination = Destination(grid_x, grid_y)
                all_sprites.add(destination)

    if destination is not None:  # Destination exists
        current_heuristic = heuristic_original  # Initialize heuristic

        if pygame.key.get_pressed()[pygame.K_SPACE]:
            current_heuristic = heuristic_obstacle_aware
            path = astar(MAP, (int(player.pos.x // TILESIZE), int(player.pos.y // TILESIZE)),
                         (int(destination.rect.x // TILESIZE), int(destination.rect.y // TILESIZE)), current_heuristic)
        elif pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]:
            current_heuristic = heuristic_original
            path = astar(MAP, (int(player.pos.x // TILESIZE), int(player.pos.y // TILESIZE)),
                         (int(destination.rect.x // TILESIZE), int(destination.rect.y // TILESIZE)), current_heuristic)

    player.update(dt, walls)
    
    # Drawing
    window.fill((255, 255, 255))

    for x in range(0, window.get_width(), TILESIZE):
        pygame.draw.line(window, (127, 127, 127), (x, 0), (x, window.get_height()))
    for y in range(0, window.get_height(), TILESIZE):
        pygame.draw.line(window, (127, 127, 127), (0, y), (window.get_width(), y))

    walls.draw(window)
    for sprite in all_sprites:
        window.blit(sprite.image, sprite.rect)

    if path:
        for x, y in path:
            pygame.draw.rect(window, (0, 255, 255), (x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE))  # Cyan for path

    pygame.display.flip()
    
pygame.quit()
