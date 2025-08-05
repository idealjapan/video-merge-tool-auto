#!/usr/bin/env python3
import random
from typing import List, Dict

class BackgroundPromptGenerator:
    """背景動画用のプロンプトをランダム生成"""
    
    # ベーススタイル（動きのある自然・動物系）
    BASE_STYLES = [
        "tropical fish swimming in aquarium",
        "butterflies flying in garden",
        "birds flying across sky",
        "ocean waves rolling on beach",
        "cherry blossom petals falling",
        "koi fish swimming in pond",
        "dolphins jumping in ocean",
        "forest leaves swaying in wind",
        "colorful tropical birds flying",
        "school of fish swimming together"
    ]
    
    # 環境・シーン（明るく安全）
    COLOR_THEMES = [
        "bright sunny day with blue sky",
        "colorful coral reef underwater",
        "green forest with sunlight",
        "clear blue ocean water",
        "spring garden with flowers",
        "peaceful lake at sunrise",
        "tropical paradise beach",
        "meadow with wildflowers",
        "crystal clear water",
        "vibrant nature colors"
    ]
    
    # 動きのパターン（動的に変更）
    MOTION_PATTERNS = [
        "actively swimming around",
        "gracefully flying through",
        "playfully jumping and diving",
        "continuously moving forward",
        "energetically fluttering",
        "smoothly gliding across",
        "dynamically interacting",
        "naturally flowing movement",
        "lively swimming patterns",
        "constant motion throughout"
    ]
    
    # 追加の効果（自然な明るさ）
    ADDITIONAL_EFFECTS = [
        "with natural sunlight",
        "with bright daylight",
        "with sparkling water effects",
        "with vivid colors",
        "with high energy movement",
        "with cheerful atmosphere",
        "with professional quality",
        "with smooth camera motion",
        "with clear visibility",
        "with positive vibes"
    ]
    
    @staticmethod
    def generate_prompt(orientation: str = "horizontal") -> str:
        """ランダムな背景プロンプトを生成"""
        
        # 各要素をランダムに選択
        style = random.choice(BackgroundPromptGenerator.BASE_STYLES)
        color = random.choice(BackgroundPromptGenerator.COLOR_THEMES)
        motion = random.choice(BackgroundPromptGenerator.MOTION_PATTERNS)
        effect = random.choice(BackgroundPromptGenerator.ADDITIONAL_EFFECTS)
        
        # アスペクト比の指定（より明確に）
        if orientation == "vertical":
            aspect = "vertical 9:16 portrait format, tall video for mobile phone screen"
        else:
            aspect = "horizontal 16:9 landscape format, wide video"
        
        # プロンプトを組み立て
        prompt = f"{style}, {color}, {motion}, {effect}, {aspect}, seamless loop, high quality, no text, no people, nature documentary style"
        
        return prompt
    
    @staticmethod
    def get_themed_prompt(theme: str, orientation: str = "horizontal") -> str:
        """テーマ指定でプロンプト生成"""
        
        themes = {
            "ocean": "underwater scene with colorful tropical fish swimming actively, coral reef, bright blue water, continuous movement",
            "sky": "blue sky with white clouds, birds flying across, butterflies fluttering, dynamic aerial movement",
            "garden": "flower garden with butterflies and bees flying around, petals falling, vibrant colors, lively atmosphere",
            "aquarium": "large aquarium with schools of fish swimming, bubbles rising, crystal clear water, constant motion",
            "nature": "forest scene with birds flying, leaves rustling, sunlight streaming through trees, wildlife activity"
        }
        
        base_prompt = themes.get(theme, themes["ocean"])
        aspect = "vertical 9:16 format" if orientation == "vertical" else "horizontal 16:9 format"
        
        return f"{base_prompt}, {aspect}, seamless loop, high quality, no text, no people"
    
    @staticmethod
    def get_random_prompts(count: int = 5, orientation: str = "horizontal") -> List[str]:
        """複数のランダムプロンプトを生成"""
        return [BackgroundPromptGenerator.generate_prompt(orientation) for _ in range(count)]


# 使用例
if __name__ == "__main__":
    generator = BackgroundPromptGenerator()
    
    print("=== ランダムプロンプト例 ===")
    for i in range(5):
        print(f"{i+1}. {generator.generate_prompt()}")
    
    print("\n=== 縦動画用プロンプト ===")
    print(generator.generate_prompt("vertical"))
    
    print("\n=== テーマ別プロンプト ===")
    for theme in ["ocean", "sky", "garden"]:
        print(f"{theme}: {generator.get_themed_prompt(theme)}")