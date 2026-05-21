File delivery fallback: when write_file and terminal are both unavailable, deliver file content inline in the response + step-by-step manual copy instructions. skill_manage write_file may work when general write_file does not (write to skill's references/ dir).
§
老板的代理记账业务受财政局和税务局联合监管。代理记账是其基础业务之一，公司注册、税务合规、高端会计咨询等业务围绕此展开。
§
Recurring issue: user is on Windows and tries to send local files (C:/D: drive) to the remote Hermes agent. The agent runs on a remote Linux server; read_file/write_file/terminal cannot access the user's local filesystem. Saved skill 'windows-user-file-transfer' for handling this pattern — alternatives: paste content, URL, WorkBuddy. Don't keep retrying local path access.
§
老板的代理记账业务核心监管文件已掌握：
1. 《涉税专业服务管理办法（试行）》（国家税务总局令第58号，2025年5月1日施行）— 代理记账机构被明确列为涉税专业服务机构，受实名制、信用码、业务信息报送、TSC信用等级等全面监管。
2. 《涉税专业服务信用评价管理办法》（国家税务总局公告2026年第1号）— 500分制TSC信用积分体系，TSC5级(400+)到TSC1级(<100)，年度评价。失信主体1年/严重失信主体2年，可申请信用修复。TSC5级享绿色通道等激励，TSC1级受双方面签、停在线服务等约束。

关键监管要点：涉税服务人员需实名认证取得信用码；业务委托协议需报送；分类管理（一般服务 vs 特定服务）；失信主体共赴现场办理；联合惩戒（通报财政、市场监督等部门）。
§
用户说"财政税务联合监管"或"联合监管"时，必须自动加载技能 bookkeeping-compliance-handbook（代理记账合规监管手册）。