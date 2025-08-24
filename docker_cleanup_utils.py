"""
도커 환경에서 TTS 파일 정리를 위한 유틸리티 함수들
"""

import os
import shutil
import logging
import time
from typing import List, Tuple, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

def safe_remove_file(file_path: str) -> Tuple[bool, str]:
    """
    도커 환경에서 안전하게 파일을 삭제하는 함수
    
    Args:
        file_path: 삭제할 파일 경로
        
    Returns:
        Tuple[bool, str]: (성공 여부, 에러 메시지 또는 성공 메시지)
    """
    try:
        if not os.path.exists(file_path):
            return True, f"File already removed: {os.path.basename(file_path)}"
        
        # 파일 정보 확인
        file_stat = os.stat(file_path)
        file_size = file_stat.st_size
        
        # 권한 조정 시도 (도커 환경에서 필요할 수 있음)
        try:
            os.chmod(file_path, 0o666)
        except PermissionError:
            pass  # 권한 변경 실패해도 삭제 시도
        
        # 파일 삭제
        os.remove(file_path)
        
        return True, f"Successfully deleted {os.path.basename(file_path)} ({file_size} bytes)"
        
    except PermissionError as e:
        return False, f"Permission denied: {e}"
    except OSError as e:
        return False, f"OS error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

def safe_remove_directory(dir_path: str, force: bool = False) -> Tuple[bool, str]:
    """
    도커 환경에서 안전하게 디렉토리를 삭제하는 함수
    
    Args:
        dir_path: 삭제할 디렉토리 경로
        force: 강제 삭제 여부
        
    Returns:
        Tuple[bool, str]: (성공 여부, 에러 메시지 또는 성공 메시지)
    """
    try:
        if not os.path.exists(dir_path):
            return True, f"Directory already removed: {dir_path}"
        
        if not os.path.isdir(dir_path):
            return False, f"Path is not a directory: {dir_path}"
        
        # 디렉토리 내용 확인
        total_files = 0
        total_size = 0
        
        for root, dirs, files in os.walk(dir_path):
            total_files += len(files)
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                except:
                    pass
        
        if force:
            # 강제 삭제: 모든 파일과 디렉토리 권한 조정
            for root, dirs, files in os.walk(dir_path, topdown=False):
                # 파일 권한 조정 및 삭제
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        os.chmod(file_path, 0o666)
                        os.remove(file_path)
                    except:
                        pass
                
                # 디렉토리 권한 조정
                for dir_name in dirs:
                    try:
                        os.chmod(os.path.join(root, dir_name), 0o777)
                    except:
                        pass
        
        # 디렉토리 삭제
        shutil.rmtree(dir_path)
        
        return True, f"Successfully removed directory with {total_files} files ({total_size} bytes)"
        
    except PermissionError as e:
        return False, f"Permission denied: {e}"
    except OSError as e:
        return False, f"OS error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

def cleanup_tts_session(tempdir: str, outputs_dir: str = "outputs") -> Dict[str, any]:
    """
    TTS 세션의 임시 파일들을 정리하는 함수
    
    Args:
        tempdir: 임시 디렉토리 이름
        outputs_dir: 출력 디렉토리 경로
        
    Returns:
        Dict: 정리 결과 정보
    """
    result = {
        "success": False,
        "deleted_files": 0,
        "deleted_size": 0,
        "errors": [],
        "warnings": []
    }
    
    try:
        # TTS 파일들이 있는 디렉토리
        tts_dir = os.path.join(outputs_dir, tempdir, "audio", "tts")
        session_dir = os.path.join(outputs_dir, tempdir)
        
        logger.info(f"🧹 Starting TTS session cleanup: {tempdir}")
        
        # 1단계: TTS 파일들 개별 삭제
        if os.path.exists(tts_dir):
            for file_name in os.listdir(tts_dir):
                if file_name.endswith(('.mp3', '.wav')):
                    file_path = os.path.join(tts_dir, file_name)
                    
                    # 파일 크기 확인
                    try:
                        file_size = os.path.getsize(file_path)
                    except:
                        file_size = 0
                    
                    # 파일 삭제
                    success, message = safe_remove_file(file_path)
                    if success:
                        result["deleted_files"] += 1
                        result["deleted_size"] += file_size
                        logger.debug(f"✅ {message}")
                    else:
                        result["errors"].append(f"File deletion failed: {file_name} - {message}")
                        logger.warning(f"❌ Failed to delete {file_name}: {message}")
        
        # 2단계: 세션 디렉토리 삭제
        if os.path.exists(session_dir):
            success, message = safe_remove_directory(session_dir, force=True)
            if success:
                logger.info(f"✅ {message}")
                result["success"] = True
            else:
                result["warnings"].append(f"Directory cleanup failed: {message}")
                logger.warning(f"⚠️  Directory cleanup failed: {message}")
                # 파일들이 삭제되었으면 부분 성공
                if result["deleted_files"] > 0:
                    result["success"] = True
        else:
            result["success"] = True
            logger.debug(f"📁 Session directory already removed: {session_dir}")
        
        # 결과 로깅
        if result["success"]:
            logger.info(f"🎉 Session cleanup completed: {result['deleted_files']} files, {result['deleted_size']} bytes")
        else:
            logger.warning(f"⚠️  Session cleanup partially failed: {len(result['errors'])} errors")
        
        return result
        
    except Exception as e:
        result["errors"].append(f"Cleanup process failed: {str(e)}")
        logger.error(f"❌ TTS session cleanup failed: {str(e)}")
        return result

def cleanup_old_combined_files(outputs_dir: str = "outputs", max_age_minutes: int = 30) -> Dict[str, any]:
    """
    오래된 결합 파일들을 정리하는 함수 (도커 스토리지 관리)
    
    Args:
        outputs_dir: 출력 디렉토리 경로
        max_age_minutes: 최대 보관 시간 (분)
        
    Returns:
        Dict: 정리 결과 정보
    """
    result = {
        "success": True,
        "deleted_files": 0,
        "deleted_size": 0,
        "errors": []
    }
    
    try:
        if not os.path.exists(outputs_dir):
            return result
        
        current_time = time.time()
        max_age_seconds = max_age_minutes * 60
        
        logger.info(f"🧹 Starting cleanup of old combined files (older than {max_age_minutes} minutes)")
        
        for file_name in os.listdir(outputs_dir):
            if file_name.startswith("combined_") and file_name.endswith(".wav"):
                file_path = os.path.join(outputs_dir, file_name)
                
                try:
                    # 파일 나이 확인
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > max_age_seconds:
                        # 파일 크기 확인
                        file_size = os.path.getsize(file_path)
                        
                        # 파일 삭제
                        success, message = safe_remove_file(file_path)
                        if success:
                            result["deleted_files"] += 1
                            result["deleted_size"] += file_size
                            logger.info(f"🗑️  Auto-cleaned old file: {file_name} ({file_size} bytes, {file_age/60:.1f} min old)")
                        else:
                            result["errors"].append(f"Failed to delete {file_name}: {message}")
                            logger.warning(f"❌ Failed to delete old file {file_name}: {message}")
                    
                except Exception as e:
                    result["errors"].append(f"Error processing {file_name}: {str(e)}")
                    logger.warning(f"⚠️  Error processing file {file_name}: {str(e)}")
        
        if result["deleted_files"] > 0:
            logger.info(f"🎉 Auto-cleanup completed: {result['deleted_files']} files, {result['deleted_size']} bytes freed")
        else:
            logger.debug("📋 No old files found for cleanup")
        
        return result
        
    except Exception as e:
        result["success"] = False
        result["errors"].append(f"Auto-cleanup failed: {str(e)}")
        logger.error(f"❌ Auto-cleanup failed: {str(e)}")
        return result

def get_docker_storage_info(outputs_dir: str = "outputs") -> Dict[str, any]:
    """
    도커 스토리지 사용량 정보를 가져오는 함수
    
    Args:
        outputs_dir: 출력 디렉토리 경로
        
    Returns:
        Dict: 스토리지 정보
    """
    info = {
        "outputs_dir_exists": False,
        "total_files": 0,
        "total_size": 0,
        "combined_files": 0,
        "combined_size": 0,
        "temp_directories": 0,
        "temp_files": 0,
        "temp_size": 0,
        "oldest_file_age_minutes": 0,
        "warnings": []
    }
    
    try:
        if not os.path.exists(outputs_dir):
            return info
        
        info["outputs_dir_exists"] = True
        current_time = time.time()
        oldest_time = current_time
        
        for item in os.listdir(outputs_dir):
            item_path = os.path.join(outputs_dir, item)
            
            if os.path.isfile(item_path):
                try:
                    file_size = os.path.getsize(item_path)
                    file_time = os.path.getmtime(item_path)
                    
                    info["total_files"] += 1
                    info["total_size"] += file_size
                    
                    if file_time < oldest_time:
                        oldest_time = file_time
                    
                    if item.startswith("combined_") and item.endswith(".wav"):
                        info["combined_files"] += 1
                        info["combined_size"] += file_size
                        
                except Exception as e:
                    info["warnings"].append(f"Error reading file {item}: {str(e)}")
                    
            elif os.path.isdir(item_path):
                info["temp_directories"] += 1
                
                # 임시 디렉토리 내 파일들 카운트
                for root, dirs, files in os.walk(item_path):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            file_size = os.path.getsize(file_path)
                            file_time = os.path.getmtime(file_path)
                            
                            info["temp_files"] += 1
                            info["temp_size"] += file_size
                            info["total_files"] += 1
                            info["total_size"] += file_size
                            
                            if file_time < oldest_time:
                                oldest_time = file_time
                                
                        except Exception as e:
                            info["warnings"].append(f"Error reading temp file {file}: {str(e)}")
        
        # 가장 오래된 파일의 나이 계산
        if oldest_time < current_time:
            info["oldest_file_age_minutes"] = (current_time - oldest_time) / 60
        
        return info
        
    except Exception as e:
        info["warnings"].append(f"Error getting storage info: {str(e)}")
        return info