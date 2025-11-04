"""
CODE996 数据看板后端接口示例实现

这是一个简单的 Flask 示例，展示如何实现数据看板所需的 API 接口。
实际开发中，需要根据具体情况调整代码逻辑。

使用方法:
1. 安装依赖: pip install flask flask-cors
2. 运行服务: python backend_example.py
3. 测试接口: curl "http://localhost:8000/api/dashboard/summary?projects=test1,test2"
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# 添加父目录到路径，以便导入 code996_local.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

# 如果需要使用现有的 code996_local.py 功能，可以这样导入
# from code996_local import analyze_repos

app = Flask(__name__)
CORS(app)  # 允许跨域请求


def get_summary_data(projects):
    """
    获取汇总数据的实际实现
    
    TODO: 这里需要实现实际的数据统计逻辑
    可以参考 code996_local.py 中的实现
    
    参数:
        projects: 项目列表
        
    返回:
        汇总数据字典
    """
    
    # 这里返回示例数据
    # 实际开发中，需要调用 code996_local.py 或实现自己的统计逻辑
    
    return {
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "total_count": 1250,
        "repo_count": len(projects),
        
        # 按小时统计 (必须 24 个元素)
        "hour_data": [
            {"time": "00", "count": 10},
            {"time": "01", "count": 5},
            {"time": "02", "count": 3},
            {"time": "03", "count": 2},
            {"time": "04", "count": 1},
            {"time": "05", "count": 4},
            {"time": "06", "count": 8},
            {"time": "07", "count": 15},
            {"time": "08", "count": 25},
            {"time": "09", "count": 80},
            {"time": "10", "count": 95},
            {"time": "11", "count": 88},
            {"time": "12", "count": 45},
            {"time": "13", "count": 60},
            {"time": "14", "count": 105},
            {"time": "15", "count": 110},
            {"time": "16", "count": 98},
            {"time": "17", "count": 85},
            {"time": "18", "count": 70},
            {"time": "19", "count": 95},
            {"time": "20", "count": 110},
            {"time": "21", "count": 125},
            {"time": "22", "count": 88},
            {"time": "23", "count": 42}
        ],
        
        # 按星期统计 (必须 7 个元素)
        "week_data": [
            {"time": "周一", "count": 220},
            {"time": "周二", "count": 195},
            {"time": "周三", "count": 210},
            {"time": "周四", "count": 185},
            {"time": "周五", "count": 175},
            {"time": "周六", "count": 125},
            {"time": "周日", "count": 140}
        ],
        
        # 工作/加班时间占比 (必须 2 个元素)
        "work_hour_pl": [
            {"time": "工作时间", "count": 650},
            {"time": "加班时间", "count": 600}
        ],
        
        # 工作日/周末占比 (必须 2 个元素)
        "work_week_pl": [
            {"time": "工作日", "count": 985},
            {"time": "周末", "count": 265}
        ],
        
        "index_996": 0.85,
        "overtime_ratio": 0.48,
        "is_standard": False
    }


def get_contributors_data(projects):
    """
    获取贡献者列表的实际实现
    
    TODO: 这里需要实现实际的贡献者统计逻辑
    
    参数:
        projects: 项目列表
        
    返回:
        贡献者列表，按 commits 降序排列
    """
    
    # 这里返回示例数据
    # 实际开发中，需要从 Git 仓库中提取实际的贡献者信息
    
    contributors = [
        {"name": "张三", "email": "zhangsan@example.com", "commits": 245, "additions": 12450, "deletions": 3200},
        {"name": "李四", "email": "lisi@example.com", "commits": 189, "additions": 9800, "deletions": 2100},
        {"name": "王五", "email": "wangwu@example.com", "commits": 156, "additions": 8900, "deletions": 1800},
        {"name": "赵六", "email": "zhaoliu@example.com", "commits": 142, "additions": 7600, "deletions": 1500},
        {"name": "钱七", "email": "qianqi@example.com", "commits": 128, "additions": 6800, "deletions": 1200},
        {"name": "孙八", "email": "sunba@example.com", "commits": 115, "additions": 5900, "deletions": 1100},
        {"name": "周九", "email": "zhoujiu@example.com", "commits": 98, "additions": 5200, "deletions": 980},
        {"name": "吴十", "email": "wushi@example.com", "commits": 87, "additions": 4500, "deletions": 850},
        {"name": "郑十一", "email": "zhengshiyi@example.com", "commits": 76, "additions": 3900, "deletions": 720},
        {"name": "王十二", "email": "wangshier@example.com", "commits": 65, "additions": 3200, "deletions": 600}
    ]
    
    # 确保按 commits 降序排列
    contributors.sort(key=lambda x: x['commits'], reverse=True)
    
    # 添加 rank 字段
    for i, contributor in enumerate(contributors, 1):
        contributor['rank'] = i
    
    return contributors


@app.route('/api/dashboard/summary', methods=['GET'])
def get_summary():
    """
    获取汇总数据接口
    
    请求: GET /api/dashboard/summary?projects=project1,project2,project3
    响应: JSON 格式的汇总数据
    """
    try:
        # 获取项目列表参数
        projects_param = request.args.get('projects', '')
        
        if not projects_param:
            return jsonify({
                "code": 400,
                "message": "参数错误: projects 参数不能为空",
                "data": None
            }), 400
        
        # 解析项目列表
        projects = [p.strip() for p in projects_param.split(',') if p.strip()]
        
        if not projects:
            return jsonify({
                "code": 400,
                "message": "参数错误: projects 参数格式不正确",
                "data": None
            }), 400
        
        print(f"正在处理项目: {projects}")
        
        # 获取汇总数据
        data = get_summary_data(projects)
        
        return jsonify({
            "code": 200,
            "message": "success",
            "data": data
        })
        
    except Exception as e:
        print(f"错误: {e}")
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500


@app.route('/api/dashboard/contributors', methods=['GET'])
def get_contributors():
    """
    获取贡献者列表接口
    
    请求: GET /api/dashboard/contributors?projects=project1,project2,project3
    响应: JSON 格式的贡献者列表
    """
    try:
        # 获取项目列表参数
        projects_param = request.args.get('projects', '')
        
        if not projects_param:
            return jsonify({
                "code": 400,
                "message": "参数错误: projects 参数不能为空",
                "data": None
            }), 400
        
        # 解析项目列表
        projects = [p.strip() for p in projects_param.split(',') if p.strip()]
        
        if not projects:
            return jsonify({
                "code": 400,
                "message": "参数错误: projects 参数格式不正确",
                "data": None
            }), 400
        
        print(f"正在获取贡献者: {projects}")
        
        # 获取贡献者列表
        data = get_contributors_data(projects)
        
        return jsonify({
            "code": 200,
            "message": "success",
            "data": data
        })
        
    except Exception as e:
        print(f"错误: {e}")
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "ok",
        "message": "服务运行正常"
    })


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        "code": 404,
        "message": "接口不存在",
        "data": None
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({
        "code": 500,
        "message": "服务器内部错误",
        "data": None
    }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("CODE996 数据看板后端服务")
    print("=" * 60)
    print("")
    print("服务地址: http://localhost:8000")
    print("")
    print("可用接口:")
    print("  1. GET /api/dashboard/summary?projects=xxx")
    print("  2. GET /api/dashboard/contributors?projects=xxx")
    print("  3. GET /health")
    print("")
    print("测试命令:")
    print('  curl "http://localhost:8000/api/dashboard/summary?projects=test1,test2"')
    print('  curl "http://localhost:8000/api/dashboard/contributors?projects=test1,test2"')
    print("")
    print("前端对接:")
    print("  修改 dashboard/src/api/dashboard.ts 中的 API_BASE")
    print('  const API_BASE = "http://localhost:8000/api/dashboard"')
    print("")
    print("=" * 60)
    print("")
    
    # 启动服务
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )

