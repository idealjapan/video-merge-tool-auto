#!/usr/bin/env python3
"""
広告グループ名パーサーのストレステスト
様々なパターンで動作を検証
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from automation.google_drive_finder import GoogleDriveFinder

def test_parser():
    """パーサーのストレステスト"""
    
    # テスト用のインスタンス作成（フォルダIDは適当でOK）
    finder = GoogleDriveFinder(folder_id="dummy")
    
    # テストケース定義
    test_cases = [
        # 1. 正常な形式（MCC記載あり）
        {
            "input": "YT_NB_7stepパク応援特典8選_MCC02運用02_28_01",
            "expected_project": "NB",
            "expected_video": "7stepパク応援特典8選",
            "expected_has_mcc": True,
            "description": "正常形式（短い動画名、MCC記載あり）"
        },
        {
            "input": "YT_OM_売れっ子イラストレーター_撮影06_お家で趣味のイラストをお仕事にする_MCC02運用46_03_01",
            "expected_project": "OM",
            "expected_video": "売れっ子イラストレーター_撮影06_お家で趣味のイラストをお仕事にする",
            "expected_has_mcc": True,
            "description": "正常形式（撮影番号あり、MCC記載あり）"
        },
        
        # 2. MCC記載漏れ
        {
            "input": "YT_NB_老後は考えるな_撮影01_老後のことひとりで考えていませんか？_AIツール素材をフリー素材に_01_01",
            "expected_project": "NB",
            "expected_video": "老後は考えるな_撮影01_老後のことひとりで考えていませんか？_AIツール素材をフリー素材に",
            "expected_has_mcc": False,
            "description": "MCC記載漏れ（特記事項あり）"
        },
        {
            "input": "YT_SBC_ビジネスコンセプト_撮影03_説明文_備考_02_01",
            "expected_project": "SBC",
            "expected_video": "ビジネスコンセプト_撮影03_説明文_備考",
            "expected_has_mcc": False,
            "description": "MCC記載漏れ（複数の特記事項）"
        },
        
        # 3. 様々な数字パターン
        {
            "input": "YT_NB_テスト動画_55_69",
            "expected_project": "NB",
            "expected_video": "テスト動画",
            "expected_has_mcc": False,
            "description": "大きな数字（55_69）"
        },
        {
            "input": "YT_OM_サンプル_123_456_789",
            "expected_project": "OM",
            "expected_video": "サンプル",
            "expected_has_mcc": False,
            "description": "3つの数字パート（123_456_789）"
        },
        {
            "input": "YT_SBC_動画名_1_2",
            "expected_project": "SBC",
            "expected_video": "動画名",
            "expected_has_mcc": False,
            "description": "1桁の数字（1_2）"
        },
        
        # 4. エッジケース
        {
            "input": "YT_RL_数字999を含む動画名_01_01",
            "expected_project": "RL",
            "expected_video": "数字999を含む動画名",
            "expected_has_mcc": False,
            "description": "動画名に数字を含む"
        },
        {
            "input": "YT_NB_ver02_改善版_テスト_03_04",
            "expected_project": "NB",
            "expected_video": "ver02_改善版_テスト",
            "expected_has_mcc": False,
            "description": "動画名の最初に数字付きパート"
        },
        {
            "input": "YT_OM_動画_MCC_偽物_01_02",
            "expected_project": "OM",
            "expected_video": "動画",
            "expected_has_mcc": True,
            "description": "MCC文字列が複数箇所に存在"
        },
        
        # 5. 特殊文字を含むケース
        {
            "input": "YT_NB_【特別版】動画タイトル_撮影01_説明_01_02",
            "expected_project": "NB",
            "expected_video": "【特別版】動画タイトル_撮影01_説明",
            "expected_has_mcc": False,
            "description": "括弧を含む動画名"
        },
        {
            "input": "YT_SBC_動画（テスト）_ver.2.1_詳細_MCC03運用_05_06",
            "expected_project": "SBC",
            "expected_video": "動画（テスト）_ver.2.1_詳細",
            "expected_has_mcc": True,
            "description": "括弧とピリオドを含む"
        },
        
        # 6. 境界値テスト
        {
            "input": "YT_A_B_1_2",
            "expected_project": "A",
            "expected_video": "B",
            "expected_has_mcc": False,
            "description": "最小構成"
        },
        {
            "input": "YT_PROJECT_" + "_".join(["パート" + str(i) for i in range(10)]) + "_01_02",
            "expected_project": "PROJECT",
            "expected_video": "_".join(["パート" + str(i) for i in range(10)]),
            "expected_has_mcc": False,
            "description": "非常に長い動画名"
        },
        
        # 7. 不正な形式
        {
            "input": "NB_動画名_01_02",
            "expected_project": "NB",
            "expected_video": "動画名_01_02",
            "expected_has_mcc": False,
            "description": "YTプレフィックスなし"
        },
        {
            "input": "YT_NB",
            "expected_project": "NB",
            "expected_video": "",
            "expected_has_mcc": False,
            "description": "動画名なし"
        },
        {
            "input": "完全に異なる形式",
            "expected_project": "",
            "expected_video": "完全に異なる形式",
            "expected_has_mcc": False,
            "description": "完全に異なる形式"
        },
        
        # 8. 実際のパターン追加
        {
            "input": "YT_NB_老後は考えるな_撮影01_老後のことひとりで考えていませんか？_AIツール素材をフリー素材に_MCC02運用_01_01",
            "expected_project": "NB",
            "expected_video": "老後は考えるな_撮影01_老後のことひとりで考えていませんか？_AIツール素材をフリー素材に",
            "expected_has_mcc": True,
            "description": "MCC記載ありで特記事項も含む"
        },
        {
            "input": "YT_OM_テイク03_説明文_補足情報_追加メモ_99_100",
            "expected_project": "OM",
            "expected_video": "テイク03_説明文_補足情報_追加メモ",
            "expected_has_mcc": False,
            "description": "テイク番号付き、複数の補足情報"
        },
    ]
    
    # テスト実行
    print("=" * 80)
    print("広告グループ名パーサー ストレステスト")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[テスト {i}] {test['description']}")
        print(f"入力: {test['input']}")
        
        # パース実行
        result = finder.parse_ad_group_name(test['input'])
        
        # 検証
        errors = []
        
        if result['project'] != test['expected_project']:
            errors.append(f"  ❌ プロジェクト: 期待値={test['expected_project']}, 実際={result['project']}")
        
        if result['video_name'] != test['expected_video']:
            errors.append(f"  ❌ 動画名: 期待値={test['expected_video']}, 実際={result['video_name']}")
        
        if result.get('has_mcc', False) != test['expected_has_mcc']:
            errors.append(f"  ❌ MCC有無: 期待値={test['expected_has_mcc']}, 実際={result.get('has_mcc', False)}")
        
        if errors:
            failed += 1
            print("結果: ❌ 失敗")
            for error in errors:
                print(error)
        else:
            passed += 1
            print("結果: ✅ 成功")
            print(f"  プロジェクト: {result['project']}")
            print(f"  動画名: {result['video_name']}")
            print(f"  MCC有無: {result.get('has_mcc', False)}")
    
    # サマリー
    print("\n" + "=" * 80)
    print("テスト結果サマリー")
    print("=" * 80)
    print(f"総テスト数: {len(test_cases)}")
    print(f"成功: {passed}")
    print(f"失敗: {failed}")
    
    if failed == 0:
        print("\n🎉 すべてのテストが成功しました！")
    else:
        print(f"\n⚠️ {failed}個のテストが失敗しました。")
        sys.exit(1)

if __name__ == "__main__":
    test_parser()