#!/usr/bin/env python3
"""
改善された広告グループ名パーサー
MCCの記載漏れにも対応
"""

import re

def parse_ad_group_name_improved(ad_group_name: str) -> dict:
    """
    広告グループ名を解析（改善版）
    
    正しい形式：
    YT_案件名_コンセプト名_撮影番号_冒頭台本_その他特記事項_MCC02運用XX_XX_XX
    
    つけ忘れの形式：
    YT_案件名_コンセプト名_撮影番号_冒頭台本_その他特記事項_XX_XX
    
    Examples:
        >>> parse_ad_group_name_improved("YT_NB_7stepパク応援特典8選_MCC02運用02_28_01")
        {'project': 'NB', 'concept': '7stepパク応援特典8選', 'video_name': '7stepパク応援特典8選', 'has_mcc': True}
        
        >>> parse_ad_group_name_improved("YT_NB_老後は考えるな_撮影01_老後のことひとりで考えていませんか？_AIツール素材をフリー素材に_01_01")
        {'project': 'NB', 'concept': '老後は考えるな', 'video_name': '老後は考えるな_撮影01_老後のことひとりで考えていませんか？', 'has_mcc': False}
    """
    
    parts = ad_group_name.split('_')
    
    # 基本的な検証
    if len(parts) < 3 or parts[0] != 'YT':
        return {
            'project': parts[0] if parts else '',
            'concept': '',
            'video_name': '_'.join(parts[1:]) if len(parts) > 1 else ad_group_name,
            'has_mcc': False,
            'full_name': ad_group_name
        }
    
    # YT_案件名_以降を解析
    project = parts[1]  # NB, OM, SBC, RL
    
    # MCCが含まれているか確認
    has_mcc = any('MCC' in part for part in parts)
    
    # 末尾の数字パターンを検出（_数字_数字 または _数字_数字_数字）
    # これは広告の階層構造を示す番号
    trailing_number_pattern = re.compile(r'^\d+$')
    
    # 後ろから数字だけの部分を特定
    trailing_numbers = []
    for i in range(len(parts) - 1, 1, -1):  # YTと案件名は除外
        if trailing_number_pattern.match(parts[i]):
            trailing_numbers.insert(0, parts[i])
        else:
            break
    
    # MCCまたは末尾の数字の前までを動画名として扱う
    video_name_parts = []
    concept = None
    
    for i, part in enumerate(parts[2:], 2):  # YTと案件名の後から
        # MCC部分に到達したら終了
        if 'MCC' in part:
            break
        # 末尾の数字部分に到達したら終了
        if trailing_numbers and i >= len(parts) - len(trailing_numbers):
            break
        
        # コンセプト名を取得（最初の要素）
        if concept is None:
            concept = part
        
        video_name_parts.append(part)
    
    video_name = '_'.join(video_name_parts)
    
    # 撮影番号を含む完全な動画名を構築
    # コンセプト名_撮影XX_冒頭台本 の形式を想定
    if '撮影' in video_name:
        # 撮影番号を含む部分まで取得
        shooting_parts = []
        found_shooting = False
        for part in video_name_parts:
            shooting_parts.append(part)
            if '撮影' in part:
                found_shooting = True
            elif found_shooting:
                # 撮影番号の次の部分（冒頭台本）も含める
                break
        if shooting_parts:
            primary_video_name = '_'.join(shooting_parts)
        else:
            primary_video_name = video_name
    else:
        primary_video_name = video_name
    
    return {
        'project': project,
        'concept': concept or '',
        'video_name': video_name,
        'primary_video_name': primary_video_name,  # 検索用の主要な動画名
        'has_mcc': has_mcc,
        'full_name': ad_group_name,
        'trailing_numbers': trailing_numbers
    }

def test_parser():
    """パーサーのテスト"""
    test_cases = [
        # 正しい形式
        "YT_NB_7stepパク応援特典8選_MCC02運用02_28_01",
        "YT_OM_売れっ子イラストレーター_撮影06_お家で趣味のイラストをお仕事にする_MCC02運用46_03_01",
        
        # MCCつけ忘れ
        "YT_NB_老後は考えるな_撮影01_老後のことひとりで考えていませんか？_AIツール素材をフリー素材に_01_01",
        "YT_SBC_ビジネスコンセプト_撮影03_説明文_備考_02_01",
        
        # 新しい命名規則
        "7StepFC_撮影01_50歳から始める在宅一人起業の応援特典8選_ニュース風編集",
    ]
    
    for test_case in test_cases:
        print(f"\n入力: {test_case}")
        result = parse_ad_group_name_improved(test_case)
        print(f"  案件: {result['project']}")
        print(f"  コンセプト: {result['concept']}")
        print(f"  動画名: {result['video_name']}")
        print(f"  主要動画名: {result.get('primary_video_name', '')}")
        print(f"  MCC有無: {result['has_mcc']}")
        if result.get('trailing_numbers'):
            print(f"  末尾番号: {result['trailing_numbers']}")

if __name__ == "__main__":
    test_parser()