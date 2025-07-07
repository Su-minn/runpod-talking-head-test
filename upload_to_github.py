#!/usr/bin/env python3
"""
GitHub 파일 업로드 및 Raw URL 생성 스크립트

assets 폴더의 테스트 파일들을 GitHub 리포지토리에 업로드하고
RunPod에서 사용할 수 있는 raw URL을 생성합니다.
"""

import os
import json
import base64
import requests
from typing import Dict, List

class GitHubUploader:
    def __init__(self, token: str, username: str, repo_name: str):
        """
        GitHub 업로더 초기화
        
        Args:
            token: GitHub Personal Access Token
            username: GitHub 사용자명
            repo_name: 리포지토리명
        """
        self.token = token
        self.username = username
        self.repo_name = repo_name
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def create_repo_if_not_exists(self) -> bool:
        """
        리포지토리가 없으면 생성
        
        Returns:
            성공 여부
        """
        try:
            # 리포지토리 존재 확인
            response = requests.get(
                f"{self.base_url}/repos/{self.username}/{self.repo_name}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                print(f"✅ 리포지토리 '{self.repo_name}' 이미 존재")
                return True
            elif response.status_code == 404:
                # 리포지토리 생성
                print(f"📝 리포지토리 '{self.repo_name}' 생성 중...")
                create_data = {
                    "name": self.repo_name,
                    "description": "RunPod Talking Head 테스트용 파일들",
                    "private": False,
                    "auto_init": True
                }
                
                create_response = requests.post(
                    f"{self.base_url}/user/repos",
                    headers=self.headers,
                    json=create_data
                )
                
                if create_response.status_code == 201:
                    print(f"✅ 리포지토리 '{self.repo_name}' 생성 완료")
                    return True
                else:
                    print(f"❌ 리포지토리 생성 실패: {create_response.text}")
                    return False
            else:
                print(f"❌ 리포지토리 확인 실패: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
            return False
    
    def upload_file(self, local_path: str, github_path: str) -> Dict:
        """
        파일을 GitHub에 업로드
        
        Args:
            local_path: 로컬 파일 경로
            github_path: GitHub 내 파일 경로
            
        Returns:
            업로드 결과
        """
        try:
            # 파일 읽기
            with open(local_path, 'rb') as f:
                content = f.read()
            
            # Base64 인코딩
            content_encoded = base64.b64encode(content).decode('utf-8')
            
            # 파일 크기 확인
            size_mb = len(content) / (1024 * 1024)
            if size_mb > 100:
                return {
                    "success": False,
                    "error": f"파일이 너무 큽니다 ({size_mb:.1f}MB > 100MB)"
                }
            
            print(f"📤 '{github_path}' 업로드 중... ({size_mb:.2f}MB)")
            
            # 기존 파일 확인
            check_response = requests.get(
                f"{self.base_url}/repos/{self.username}/{self.repo_name}/contents/{github_path}",
                headers=self.headers
            )
            
            upload_data = {
                "message": f"Upload {github_path}",
                "content": content_encoded
            }
            
            # 기존 파일이 있으면 SHA 추가
            if check_response.status_code == 200:
                existing_file = check_response.json()
                upload_data["sha"] = existing_file["sha"]
                print(f"   기존 파일 업데이트")
            else:
                print(f"   새 파일 생성")
            
            # 업로드
            upload_response = requests.put(
                f"{self.base_url}/repos/{self.username}/{self.repo_name}/contents/{github_path}",
                headers=self.headers,
                json=upload_data
            )
            
            if upload_response.status_code in [200, 201]:
                result = upload_response.json()
                raw_url = f"https://raw.githubusercontent.com/{self.username}/{self.repo_name}/main/{github_path}"
                
                print(f"   ✅ 업로드 성공")
                print(f"   🔗 Raw URL: {raw_url}")
                
                return {
                    "success": True,
                    "raw_url": raw_url,
                    "github_url": result["content"]["html_url"],
                    "file_size": len(content)
                }
            else:
                print(f"   ❌ 업로드 실패: {upload_response.text}")
                return {
                    "success": False,
                    "error": upload_response.text
                }
                
        except Exception as e:
            print(f"   ❌ 오류: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_assets(self, assets_dir: str = "assets") -> Dict:
        """
        assets 폴더의 모든 파일 업로드
        
        Args:
            assets_dir: assets 폴더 경로
            
        Returns:
            업로드 결과 딕셔너리
        """
        if not os.path.exists(assets_dir):
            return {
                "success": False,
                "error": f"'{assets_dir}' 폴더를 찾을 수 없습니다"
            }
        
        print(f"📁 '{assets_dir}' 폴더 스캔 중...")
        
        # 지원하는 파일 확장자
        supported_extensions = {'.png', '.jpg', '.jpeg', '.wav', '.mp3', '.mp4'}
        
        results = {}
        total_success = 0
        total_files = 0
        
        for filename in os.listdir(assets_dir):
            file_path = os.path.join(assets_dir, filename)
            
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                
                if file_ext in supported_extensions:
                    total_files += 1
                    github_path = f"assets/{filename}"
                    
                    result = self.upload_file(file_path, github_path)
                    results[filename] = result
                    
                    if result["success"]:
                        total_success += 1
                else:
                    print(f"   ⏭️  '{filename}' 건너뜀 (지원하지 않는 형식)")
        
        print(f"\n📊 업로드 완료: {total_success}/{total_files} 성공")
        
        return {
            "success": total_success > 0,
            "total_files": total_files,
            "successful_uploads": total_success,
            "results": results
        }
    
    def generate_test_urls(self, upload_results: Dict) -> Dict:
        """
        테스트에 사용할 URL 생성
        
        Args:
            upload_results: 업로드 결과
            
        Returns:
            테스트 URL 딕셔너리
        """
        urls = {}
        
        for filename, result in upload_results["results"].items():
            if result["success"]:
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    urls["image_url"] = result["raw_url"]
                elif filename.lower().endswith('.wav'):
                    urls["audio_wav_url"] = result["raw_url"]
                elif filename.lower().endswith('.mp3'):
                    urls["audio_mp3_url"] = result["raw_url"]
        
        return urls

def main():
    """메인 함수"""
    print("="*60)
    print("📤 GitHub 파일 업로드 도구")
    print("="*60)
    
    # 설정
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "")
    REPO_NAME = "runpod-talking-head-test"
    
    if not GITHUB_TOKEN or not GITHUB_USERNAME:
        print("⚠️  환경 변수 설정이 필요합니다:")
        print("export GITHUB_TOKEN='your-github-personal-access-token'")
        print("export GITHUB_USERNAME='your-github-username'")
        print("\n📝 GitHub Personal Access Token 생성 방법:")
        print("1. GitHub → Settings → Developer settings → Personal access tokens")
        print("2. Generate new token (classic)")
        print("3. 권한: repo (Full control of private repositories) 체크")
        return
    
    # 업로더 생성
    uploader = GitHubUploader(GITHUB_TOKEN, GITHUB_USERNAME, REPO_NAME)
    
    # 리포지토리 확인/생성
    if not uploader.create_repo_if_not_exists():
        print("❌ 리포지토리 설정 실패")
        return
    
    # 파일 업로드
    upload_results = uploader.upload_assets()
    
    if upload_results["success"]:
        # 테스트 URL 생성
        test_urls = uploader.generate_test_urls(upload_results)
        
        print("\n" + "="*60)
        print("🔗 테스트용 URL 생성 완료")
        print("="*60)
        
        for url_type, url in test_urls.items():
            print(f"{url_type}: {url}")
        
        # URL 정보를 파일로 저장
        url_info = {
            "repository": f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}",
            "test_urls": test_urls,
            "upload_results": upload_results
        }
        
        with open("github_urls.json", "w", encoding="utf-8") as f:
            json.dump(url_info, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 URL 정보 저장됨: github_urls.json")
        
        # test_comparison.py 업데이트를 위한 가이드
        print("\n📝 다음 단계:")
        print("1. test_comparison.py 파일에서 다음 URL들을 업데이트하세요:")
        for url_type, url in test_urls.items():
            print(f"   {url_type.upper()} = \"{url}\"")
        print("2. Docker 이미지를 빌드하고 RunPod에 배포하세요")
        print("3. 환경 변수를 설정하고 테스트를 실행하세요")
        
    else:
        print("❌ 파일 업로드 실패")

if __name__ == "__main__":
    main() 