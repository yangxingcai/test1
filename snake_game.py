import pygame
import random
import sys

# 初始化pygame
pygame.init()

# 游戏常量
GRID_WIDTH = 20
GRID_HEIGHT = 15
CELL_SIZE = 30
GRID_X_OFFSET = 50
GRID_Y_OFFSET = 50

# 苹果设计规范颜色系统
# 背景色
BACKGROUND_PRIMARY = (242, 242, 247)  # iOS系统背景色
BACKGROUND_SECONDARY = (255, 255, 255)  # 卡片背景色
BACKGROUND_TERTIARY = (229, 229, 234)  # 分组背景色

# 文字颜色
LABEL_PRIMARY = (0, 0, 0)  # 主要文字
LABEL_SECONDARY = (60, 60, 67)  # 次要文字
LABEL_TERTIARY = (60, 60, 67, 0.6)  # 第三级文字

# 系统颜色
SYSTEM_BLUE = (0, 122, 255)
SYSTEM_GREEN = (52, 199, 89)
SYSTEM_ORANGE = (255, 149, 0)
SYSTEM_RED = (255, 59, 48)
SYSTEM_PURPLE = (175, 82, 222)
SYSTEM_YELLOW = (255, 204, 0)
SYSTEM_PINK = (255, 45, 85)

# 游戏颜色
SNAKE_HEAD = SYSTEM_GREEN
SNAKE_BODY = (40, 180, 60)
FOOD_COLOR = SYSTEM_RED
GRID_COLOR = (142, 142, 147)
WHITE = (255, 255, 255)

# 边框和分割线
SEPARATOR = (198, 198, 200)
FILL = (120, 120, 128, 0.2)

# 方向常量
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class SnakeGame:
    def __init__(self):
        # 苹果设计规范：更大的窗口，更好的比例
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("贪吃蛇")
        self.clock = pygame.time.Clock()
        
        # 游戏状态
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.move_time = 0
        self.move_speed = 200  # 毫秒
        
        # 苹果设计规范字体系统
        try:
            # 尝试使用系统字体（苹果风格）
            self.title_font = pygame.font.Font(None, 48)  # 大标题
            self.headline_font = pygame.font.Font(None, 32)  # 标题
            self.body_font = pygame.font.Font(None, 20)  # 正文
            self.caption_font = pygame.font.Font(None, 16)  # 说明文字
        except:
            # 备用字体
            self.title_font = pygame.font.Font(None, 36)
            self.headline_font = pygame.font.Font(None, 28)
            self.body_font = pygame.font.Font(None, 18)
            self.caption_font = pygame.font.Font(None, 14)
    
    def generate_food(self):
        """生成食物位置"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                return (x, y)
    
    def move_snake(self):
        """移动贪吃蛇"""
        if self.game_over or self.paused:
            return
        
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # 检查边界碰撞
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            self.game_over = True
            return
        
        # 检查自身碰撞
        if new_head in self.snake:
            self.game_over = True
            return
        
        self.snake.insert(0, new_head)
        
        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
            # 增加游戏速度
            self.move_speed = max(100, self.move_speed - 5)
        else:
            self.snake.pop()
    
    def change_direction(self, new_direction):
        """改变蛇的方向"""
        # 防止蛇反向移动
        if (self.direction[0] * -1, self.direction[1] * -1) != new_direction:
            self.direction = new_direction
    
    def draw_grid(self):
        """绘制游戏网格"""
        # 苹果设计规范：绘制游戏区域背景
        game_area_rect = pygame.Rect(
            GRID_X_OFFSET - 5,
            GRID_Y_OFFSET - 5,
            GRID_WIDTH * CELL_SIZE + 10,
            GRID_HEIGHT * CELL_SIZE + 10
        )
        pygame.draw.rect(self.screen, BACKGROUND_SECONDARY, game_area_rect, border_radius=12)
        pygame.draw.rect(self.screen, SEPARATOR, game_area_rect, 2, border_radius=12)
        
        # 绘制网格线
        for x in range(GRID_WIDTH + 1):
            start_pos = (GRID_X_OFFSET + x * CELL_SIZE, GRID_Y_OFFSET)
            end_pos = (GRID_X_OFFSET + x * CELL_SIZE, GRID_Y_OFFSET + GRID_HEIGHT * CELL_SIZE)
            pygame.draw.line(self.screen, SEPARATOR, start_pos, end_pos, 1)
        
        for y in range(GRID_HEIGHT + 1):
            start_pos = (GRID_X_OFFSET, GRID_Y_OFFSET + y * CELL_SIZE)
            end_pos = (GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE, GRID_Y_OFFSET + y * CELL_SIZE)
            pygame.draw.line(self.screen, SEPARATOR, start_pos, end_pos, 1)
    
    def draw_snake(self):
        """绘制贪吃蛇"""
        for i, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(
                GRID_X_OFFSET + x * CELL_SIZE + 2,
                GRID_Y_OFFSET + y * CELL_SIZE + 2,
                CELL_SIZE - 4,
                CELL_SIZE - 4
            )
            
            if i == 0:  # 蛇头
                pygame.draw.rect(self.screen, SNAKE_HEAD, rect, border_radius=8)
                pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=8)
            else:  # 蛇身
                pygame.draw.rect(self.screen, SNAKE_BODY, rect, border_radius=6)
                pygame.draw.rect(self.screen, WHITE, rect, 1, border_radius=6)
    
    def draw_food(self):
        """绘制食物"""
        x, y = self.food
        rect = pygame.Rect(
            GRID_X_OFFSET + x * CELL_SIZE + 4,
            GRID_Y_OFFSET + y * CELL_SIZE + 4,
            CELL_SIZE - 8,
            CELL_SIZE - 8
        )
        pygame.draw.rect(self.screen, FOOD_COLOR, rect, border_radius=12)
        pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=12)
    
    def draw_info(self):
        """绘制游戏信息"""
        # 苹果设计规范：绘制信息卡片
        info_x = GRID_X_OFFSET + GRID_WIDTH * CELL_SIZE + 30
        info_y = GRID_Y_OFFSET + 50
        
        # 分数卡片
        score_card = pygame.Rect(info_x - 10, info_y - 10, 160, 100)
        pygame.draw.rect(self.screen, BACKGROUND_SECONDARY, score_card, border_radius=12)
        pygame.draw.rect(self.screen, SEPARATOR, score_card, 1, border_radius=12)
        
        # 分数信息
        score_text = self.headline_font.render(f"{self.score:,}", True, SYSTEM_BLUE)
        score_label = self.caption_font.render("分数", True, LABEL_SECONDARY)
        length_text = self.body_font.render(f"长度: {len(self.snake)}", True, LABEL_PRIMARY)
        
        self.screen.blit(score_label, (info_x, info_y))
        score_rect = score_text.get_rect(center=(info_x + 70, info_y + 25))
        self.screen.blit(score_text, score_rect)
        self.screen.blit(length_text, (info_x, info_y + 55))
        
        # 控制说明卡片
        controls_y = info_y + 120
        controls_card = pygame.Rect(info_x - 10, controls_y - 10, 160, 200)
        pygame.draw.rect(self.screen, BACKGROUND_SECONDARY, controls_card, border_radius=12)
        pygame.draw.rect(self.screen, SEPARATOR, controls_card, 1, border_radius=12)
        
        controls_title = self.headline_font.render("控制", True, LABEL_PRIMARY)
        title_rect = controls_title.get_rect(center=(info_x + 70, controls_y + 10))
        self.screen.blit(controls_title, title_rect)
        
        controls = [
            ("↑ ↓ ← →", "移动"),
            ("空格", "暂停"),
            ("R", "重新开始"),
            ("ESC", "退出")
        ]
        
        for i, (key, desc) in enumerate(controls):
            key_text = self.body_font.render(key, True, SYSTEM_BLUE)
            desc_text = self.caption_font.render(desc, True, LABEL_SECONDARY)
            self.screen.blit(key_text, (info_x, controls_y + 35 + i * 25))
            self.screen.blit(desc_text, (info_x, controls_y + 35 + i * 25 + 20))
    
    def draw_game_over(self):
        """绘制游戏结束界面"""
        # 苹果设计规范：绘制游戏结束模态框
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 模态框
        modal_width = 400
        modal_height = 300
        modal_x = (self.width - modal_width) // 2
        modal_y = (self.height - modal_height) // 2
        
        modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)
        pygame.draw.rect(self.screen, BACKGROUND_SECONDARY, modal_rect, border_radius=20)
        pygame.draw.rect(self.screen, SEPARATOR, modal_rect, 2, border_radius=20)
        
        # 游戏结束文本
        game_over_text = self.title_font.render("游戏结束", True, LABEL_PRIMARY)
        score_text = self.headline_font.render(f"最终分数: {self.score:,}", True, SYSTEM_BLUE)
        length_text = self.body_font.render(f"蛇的长度: {len(self.snake)}", True, LABEL_SECONDARY)
        restart_text = self.body_font.render("按 R 重新开始", True, LABEL_SECONDARY)
        exit_text = self.body_font.render("按 ESC 退出", True, LABEL_SECONDARY)
        
        game_over_rect = game_over_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 60))
        score_rect = score_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 110))
        length_rect = length_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 140))
        restart_rect = restart_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 180))
        exit_rect = exit_text.get_rect(center=(modal_x + modal_width // 2, modal_y + 210))
        
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(length_text, length_rect)
        self.screen.blit(restart_text, restart_rect)
        self.screen.blit(exit_text, exit_rect)
    
    def draw_pause(self):
        """绘制暂停界面"""
        # 苹果设计规范：绘制暂停界面
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 暂停文本
        pause_text = self.title_font.render("游戏暂停", True, LABEL_PRIMARY)
        resume_text = self.body_font.render("按空格继续游戏", True, LABEL_SECONDARY)
        
        pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2 - 20))
        resume_rect = resume_text.get_rect(center=(self.width // 2, self.height // 2 + 20))
        
        self.screen.blit(pause_text, pause_rect)
        self.screen.blit(resume_text, resume_rect)
    
    def reset_game(self):
        """重置游戏"""
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.move_speed = 200
    
    def run(self):
        """运行游戏主循环"""
        running = True
        
        while running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                    else:
                        if event.key == pygame.K_SPACE:
                            self.paused = not self.paused
                        elif not self.paused:
                            if event.key == pygame.K_UP:
                                self.change_direction(UP)
                            elif event.key == pygame.K_DOWN:
                                self.change_direction(DOWN)
                            elif event.key == pygame.K_LEFT:
                                self.change_direction(LEFT)
                            elif event.key == pygame.K_RIGHT:
                                self.change_direction(RIGHT)
                            elif event.key == pygame.K_ESCAPE:
                                running = False
                        elif event.key == pygame.K_ESCAPE:
                            running = False
            
            # 游戏逻辑更新
            if not self.game_over and not self.paused:
                if current_time - self.move_time > self.move_speed:
                    self.move_snake()
                    self.move_time = current_time
            
            # 绘制游戏
            self.screen.fill(BACKGROUND_PRIMARY)
            self.draw_grid()
            self.draw_food()
            self.draw_snake()
            self.draw_info()
            
            if self.game_over:
                self.draw_game_over()
            elif self.paused:
                self.draw_pause()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
