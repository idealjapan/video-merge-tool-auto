/**
 * キューベース広告差し替えシステム v2
 * Python側から追加されたキューを処理し、Google Adsに広告を作成
 */

// 設定
const QUEUE_CONFIG = {
  SPREADSHEET_ID: '1MdDrJFrzkz1N6ccgZN2mhL_SGh0a7qUKBJJ5B6gm70U',
  QUEUE_SHEET_NAME: '広告キュー',  // Python側のシート名と一致
  MAX_RETRIES: 3,
  BATCH_SIZE: 3  // 一度に処理する最大数（YouTubeの保留問題を考慮）
};

/**
 * メイン処理 - トリガーで定期実行される
 */
function processQueueFromSheets() {
  console.log('=== キュー処理開始 ===');
  const startTime = new Date();
  
  try {
    const processor = new QueueProcessor();
    const results = processor.processQueue();
    
    // 処理結果をログ出力
    console.log(`処理完了: ${results.processed}件処理, ${results.success}件成功, ${results.failed}件失敗`);
    
    // 処理があった場合のみ通知
    if (results.processed > 0) {
      sendProcessingNotification(results);
    }
    
  } catch (error) {
    console.error('キュー処理エラー:', error);
    sendErrorNotification('キュー処理エラー', error.toString());
  }
  
  const processingTime = (new Date() - startTime) / 1000;
  console.log(`処理時間: ${processingTime}秒`);
}

/**
 * キュー処理クラス
 */
class QueueProcessor {
  constructor() {
    this.spreadsheet = SpreadsheetApp.openById(QUEUE_CONFIG.SPREADSHEET_ID);
    this.queueSheet = this.spreadsheet.getSheetByName(QUEUE_CONFIG.QUEUE_SHEET_NAME);
    
    if (!this.queueSheet) {
      // シートがない場合は作成
      this.createQueueSheet();
    }
  }
  
  /**
   * キューシートを作成
   */
  createQueueSheet() {
    this.queueSheet = this.spreadsheet.insertSheet(QUEUE_CONFIG.QUEUE_SHEET_NAME);
    
    // ヘッダー設定
    const headers = [
      '処理ID', 'ステータス', '作成日時', '処理開始日時', '完了日時',
      '動画URL', '案件名', '広告名', '動画名', 'リトライ回数',
      'エラーメッセージ', '処理結果', '新広告ID', '処理時間(秒)', 'メタデータ'
    ];
    
    this.queueSheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    this.queueSheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
  }
  
  /**
   * キューを処理
   */
  processQueue() {
    const results = {
      processed: 0,
      success: 0,
      failed: 0,
      details: []
    };
    
    // 待機中タスクを取得
    const pendingTasks = this.getPendingTasks(QUEUE_CONFIG.BATCH_SIZE);
    
    if (pendingTasks.length === 0) {
      console.log('処理待ちタスクはありません');
      return results;
    }
    
    console.log(`${pendingTasks.length}件のタスクを処理します`);
    
    // 各タスクを処理
    for (const task of pendingTasks) {
      // TESTモードチェック
      if (task.adName && task.adName.startsWith('TEST_')) {
        console.log(`テストモード: ${task.adName}`);
        const testResult = this.processTestTask(task);
        results.processed++;
        results.success++;
        results.details.push(testResult);
        continue;
      }
      
      // 本番処理
      const taskResult = this.processTask(task);
      results.processed++;
      
      if (taskResult.success) {
        results.success++;
      } else {
        results.failed++;
      }
      
      results.details.push(taskResult);
      
      // 処理間隔を空ける（YouTubeの負荷軽減）
      Utilities.sleep(2000);  // 2秒待機
    }
    
    return results;
  }
  
  /**
   * 待機中タスクを取得
   */
  getPendingTasks(limit) {
    const dataRange = this.queueSheet.getDataRange();
    const values = dataRange.getValues();
    
    if (values.length <= 1) {
      return [];  // ヘッダーのみ
    }
    
    const tasks = [];
    const headers = values[0];
    
    // 列インデックスを取得
    const colIndex = {
      processId: headers.indexOf('処理ID'),
      status: headers.indexOf('ステータス'),
      videoUrl: headers.indexOf('動画URL'),
      projectName: headers.indexOf('案件名'),
      adName: headers.indexOf('広告名'),
      videoName: headers.indexOf('動画名'),
      retryCount: headers.indexOf('リトライ回数'),
      metadata: headers.indexOf('メタデータ')
    };
    
    // データ行を処理
    for (let i = 1; i < values.length && tasks.length < limit; i++) {
      const row = values[i];
      const status = row[colIndex.status];
      const retryCount = row[colIndex.retryCount] || 0;
      
      // 待機中状態で、リトライ上限に達していないタスクを選択
      if (status === '待機中' && retryCount < QUEUE_CONFIG.MAX_RETRIES) {
        tasks.push({
          rowIndex: i + 1,  // スプレッドシートの行番号（1-indexed）
          processId: row[colIndex.processId],
          videoUrl: row[colIndex.videoUrl],
          projectName: row[colIndex.projectName],
          adName: row[colIndex.adName],
          videoName: row[colIndex.videoName] || row[colIndex.adName],
          retryCount: retryCount,
          metadata: row[colIndex.metadata] ? 
            (typeof row[colIndex.metadata] === 'string' ? 
              JSON.parse(row[colIndex.metadata]) : row[colIndex.metadata]) 
            : {}
        });
      }
    }
    
    return tasks;
  }
  
  /**
   * テストタスクを処理
   */
  processTestTask(task) {
    console.log(`テストタスク処理: ${task.processId}`);
    
    const startTime = new Date();
    
    // ステータスを「処理中」に更新
    this.updateTaskStatus(task.rowIndex, '処理中', startTime);
    
    // テスト処理（実際には何もしない）
    Utilities.sleep(1000);  // 1秒待機してシミュレート
    
    const processingTime = (new Date() - startTime) / 1000;
    
    // ステータスを「完了」に更新
    this.updateTaskComplete(task.rowIndex, 'TEST_AD_' + Date.now(), processingTime);
    
    console.log(`✅ テスト処理成功: ${task.processId}`);
    
    return {
      processId: task.processId,
      adName: task.adName,
      success: true,
      error: null,
      newAdId: 'TEST_AD_' + Date.now()
    };
  }
  
  /**
   * 個別タスクを処理
   */
  processTask(task) {
    console.log(`\n処理開始: ${task.processId}`);
    console.log(`  案件: ${task.projectName}`);
    console.log(`  広告: ${task.adName}`);
    console.log(`  動画URL: ${task.videoUrl}`);
    
    const startTime = new Date();
    const result = {
      processId: task.processId,
      adName: task.adName,
      success: false,
      error: null,
      newAdId: null
    };
    
    try {
      // ステータスを「処理中」に更新
      this.updateTaskStatus(task.rowIndex, '処理中', startTime);
      
      // プロジェクト名から広告アカウントと広告グループを特定
      const adConfig = this.getAdConfig(task.projectName);
      
      if (!adConfig) {
        throw new Error(`案件「${task.projectName}」の設定が見つかりません`);
      }
      
      // 新しい広告を作成（実際のGoogle Ads API呼び出しはここに実装）
      // 現在はシミュレーション
      const newAdId = this.createVideoAd(
        adConfig,
        task.videoUrl,
        task.adName
      );
      
      if (!newAdId) {
        throw new Error('新しい広告の作成に失敗しました');
      }
      
      // 成功
      result.success = true;
      result.newAdId = newAdId;
      
      const processingTime = (new Date() - startTime) / 1000;
      
      // ステータスを「完了」に更新
      this.updateTaskComplete(task.rowIndex, newAdId, processingTime);
      
      console.log(`✅ 処理成功: ${task.processId} (${processingTime}秒)`);
      
    } catch (error) {
      // エラー処理
      result.error = error.toString();
      
      const processingTime = (new Date() - startTime) / 1000;
      
      // リトライ判定
      if (task.retryCount + 1 < QUEUE_CONFIG.MAX_RETRIES) {
        // リトライ可能
        this.updateTaskRetry(task.rowIndex, error.toString(), task.retryCount + 1);
        console.log(`⚠️ 処理失敗（リトライ予定）: ${task.processId} - ${error}`);
      } else {
        // リトライ上限
        this.updateTaskFailed(task.rowIndex, error.toString(), processingTime);
        console.log(`❌ 処理失敗（リトライ上限）: ${task.processId} - ${error}`);
      }
    }
    
    return result;
  }
  
  /**
   * 案件名から広告設定を取得
   */
  getAdConfig(projectName) {
    // 案件名と広告アカウント・グループのマッピング
    // 実際の設定に応じて変更
    const configs = {
      'NB': {
        accountId: 'YOUR_ACCOUNT_ID',
        campaignId: 'YOUR_CAMPAIGN_ID',
        adGroupId: 'YOUR_AD_GROUP_ID'
      },
      // 他の案件も追加
    };
    
    return configs[projectName] || null;
  }
  
  /**
   * 動画広告を作成（シミュレーション）
   */
  createVideoAd(adConfig, videoUrl, adName) {
    // 実際のGoogle Ads API呼び出しをここに実装
    // 現在はシミュレーションとして仮のIDを返す
    console.log(`広告作成シミュレーション:`);
    console.log(`  アカウント: ${adConfig.accountId}`);
    console.log(`  広告グループ: ${adConfig.adGroupId}`);
    console.log(`  動画URL: ${videoUrl}`);
    console.log(`  広告名: ${adName}`);
    
    // 仮のAD IDを生成
    return 'AD_' + Date.now();
  }
  
  /**
   * タスクステータスを更新（処理中）
   */
  updateTaskStatus(rowIndex, status, timestamp) {
    const statusCol = 2;  // B列: ステータス
    const startTimeCol = 4;  // D列: 処理開始日時
    
    this.queueSheet.getRange(rowIndex, statusCol).setValue(status);
    if (timestamp) {
      this.queueSheet.getRange(rowIndex, startTimeCol).setValue(
        Utilities.formatDate(timestamp, 'Asia/Tokyo', 'yyyy-MM-dd HH:mm:ss')
      );
    }
  }
  
  /**
   * タスク完了時の更新
   */
  updateTaskComplete(rowIndex, newAdId, processingTime) {
    const statusCol = 2;  // B列: ステータス
    const completeTimeCol = 5;  // E列: 完了日時
    const resultCol = 12;  // L列: 処理結果
    const newAdIdCol = 13;  // M列: 新広告ID
    const timeCol = 14;  // N列: 処理時間
    
    this.queueSheet.getRange(rowIndex, statusCol).setValue('完了');
    this.queueSheet.getRange(rowIndex, completeTimeCol).setValue(
      Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy-MM-dd HH:mm:ss')
    );
    this.queueSheet.getRange(rowIndex, resultCol).setValue('成功');
    this.queueSheet.getRange(rowIndex, newAdIdCol).setValue(newAdId);
    this.queueSheet.getRange(rowIndex, timeCol).setValue(processingTime);
  }
  
  /**
   * リトライ時の更新
   */
  updateTaskRetry(rowIndex, errorMessage, newRetryCount) {
    const statusCol = 2;  // B列: ステータス
    const retryCol = 10;  // J列: リトライ回数
    const errorCol = 11;  // K列: エラーメッセージ
    
    this.queueSheet.getRange(rowIndex, statusCol).setValue('待機中');  // 待機中に戻す
    this.queueSheet.getRange(rowIndex, retryCol).setValue(newRetryCount);
    this.queueSheet.getRange(rowIndex, errorCol).setValue(errorMessage);
  }
  
  /**
   * 失敗時の更新
   */
  updateTaskFailed(rowIndex, errorMessage, processingTime) {
    const statusCol = 2;  // B列: ステータス
    const completeTimeCol = 5;  // E列: 完了日時
    const errorCol = 11;  // K列: エラーメッセージ
    const resultCol = 12;  // L列: 処理結果
    const timeCol = 14;  // N列: 処理時間
    
    this.queueSheet.getRange(rowIndex, statusCol).setValue('失敗');
    this.queueSheet.getRange(rowIndex, completeTimeCol).setValue(
      Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy-MM-dd HH:mm:ss')
    );
    this.queueSheet.getRange(rowIndex, errorCol).setValue(errorMessage);
    this.queueSheet.getRange(rowIndex, resultCol).setValue('失敗');
    this.queueSheet.getRange(rowIndex, timeCol).setValue(processingTime);
  }
}

/**
 * 処理通知
 */
function sendProcessingNotification(results) {
  console.log('処理通知:', results);
  // Lark通知やメール通知を実装可能
}

/**
 * エラー通知
 */
function sendErrorNotification(title, error) {
  console.error(title, error);
  // Lark通知やメール通知を実装可能
}

/**
 * トリガー設定用関数
 */
function setupQueueTrigger() {
  // 既存のトリガーを削除
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'processQueueFromSheets') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // 新しいトリガーを作成（5分ごと）
  ScriptApp.newTrigger('processQueueFromSheets')
    .timeBased()
    .everyMinutes(5)
    .create();
  
  console.log('キュー処理トリガーを設定しました（5分ごと）');
}

/**
 * 手動テスト用
 */
function testQueueProcessing() {
  // テストデータを追加
  const spreadsheet = SpreadsheetApp.openById(QUEUE_CONFIG.SPREADSHEET_ID);
  const queueSheet = spreadsheet.getSheetByName(QUEUE_CONFIG.QUEUE_SHEET_NAME);
  
  if (queueSheet) {
    const testData = [
      'TEST_' + Date.now(),  // 処理ID
      '待機中',  // ステータス
      new Date(),  // 作成日時
      '',  // 処理開始日時
      '',  // 完了日時
      'https://www.youtube.com/watch?v=test123',  // 動画URL
      'TEST',  // 案件名
      'TEST_広告_' + Date.now(),  // 広告名
      'テスト動画',  // 動画名
      0,  // リトライ回数
      '',  // エラーメッセージ
      '',  // 処理結果
      '',  // 新広告ID
      '',  // 処理時間
      JSON.stringify({test: true})  // メタデータ
    ];
    
    queueSheet.appendRow(testData);
    console.log('テストデータを追加しました');
  }
  
  // キュー処理を実行
  processQueueFromSheets();
}