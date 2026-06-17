--
-- PostgreSQL database dump
--

\restrict 5PxxLp13VmOwQ6yD6RfOx6kZCLhavTSebbm2LlHnfy2NjzZ9fthUgMk8NVj4w19

-- Dumped from database version 17.6
-- Dumped by pg_dump version 18.0

-- Started on 2026-06-08 14:59:38

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 943 (class 1247 OID 17158)
-- Name: announcementpriority; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.announcementpriority AS ENUM (
    'low',
    'medium',
    'high',
    'urgent'
);


ALTER TYPE public.announcementpriority OWNER TO postgres;

--
-- TOC entry 946 (class 1247 OID 17168)
-- Name: announcementscope; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.announcementscope AS ENUM (
    'all',
    'role',
    'user'
);


ALTER TYPE public.announcementscope OWNER TO postgres;

--
-- TOC entry 949 (class 1247 OID 17176)
-- Name: announcementstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.announcementstatus AS ENUM (
    'draft',
    'published'
);


ALTER TYPE public.announcementstatus OWNER TO postgres;

--
-- TOC entry 940 (class 1247 OID 17150)
-- Name: announcementtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.announcementtype AS ENUM (
    'notice',
    'announcement',
    'maintenance'
);


ALTER TYPE public.announcementtype OWNER TO postgres;

--
-- TOC entry 892 (class 1247 OID 16908)
-- Name: configgroup; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.configgroup AS ENUM (
    'SYSTEM',
    'SECURITY',
    'LOG',
    'NETWORK',
    'STORAGE',
    'CUSTOM'
);


ALTER TYPE public.configgroup OWNER TO postgres;

--
-- TOC entry 889 (class 1247 OID 16897)
-- Name: configtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.configtype AS ENUM (
    'STRING',
    'NUMBER',
    'BOOLEAN',
    'JSON',
    'ARRAY'
);


ALTER TYPE public.configtype OWNER TO postgres;

--
-- TOC entry 901 (class 1247 OID 16944)
-- Name: menutype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.menutype AS ENUM (
    'CATALOG',
    'MENU',
    'BUTTON',
    'EXTERNAL'
);


ALTER TYPE public.menutype OWNER TO postgres;

--
-- TOC entry 937 (class 1247 OID 17120)
-- Name: notificationtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.notificationtype AS ENUM (
    'system',
    'approval',
    'operation',
    'remind'
);


ALTER TYPE public.notificationtype OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 217 (class 1259 OID 16881)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16887)
-- Name: app_user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.app_user (
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    phone_code character varying(10) NOT NULL,
    phone character varying(13) NOT NULL,
    password character varying(255),
    email character varying(255),
    wx_openid character varying(255),
    wx_unionid character varying(255),
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.app_user OWNER TO postgres;

--
-- TOC entry 5105 (class 0 OID 0)
-- Dependencies: 219
-- Name: TABLE app_user; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.app_user IS '
    用户表 - 存储用户信息
    ';


--
-- TOC entry 5106 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN app_user.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_user.id IS '雪花算法主键 ID';


--
-- TOC entry 5107 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN app_user.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_user.name IS '用户名';


--
-- TOC entry 5108 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN app_user.phone_code; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_user.phone_code IS '手机号区号，如：+86、+1 等';


--
-- TOC entry 5109 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN app_user.phone; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_user.phone IS '手机号';


--
-- TOC entry 5110 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN app_user.password; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_user.password IS '密码哈希值';


--
-- TOC entry 5111 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN app_user.email; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_user.email IS '邮箱';


--
-- TOC entry 5112 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN app_user.wx_openid; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_user.wx_openid IS '微信 openid';


--
-- TOC entry 5113 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN app_user.wx_unionid; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_user.wx_unionid IS '微信 unionid';


--
-- TOC entry 5114 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN app_user.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_user.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5115 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN app_user.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_user.created_at IS '创建时间';


--
-- TOC entry 5116 (class 0 OID 0)
-- Dependencies: 219
-- Name: COLUMN app_user.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.app_user.updated_at IS '更新时间';


--
-- TOC entry 218 (class 1259 OID 16886)
-- Name: app_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.app_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.app_user_id_seq OWNER TO postgres;

--
-- TOC entry 5117 (class 0 OID 0)
-- Dependencies: 218
-- Name: app_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.app_user_id_seq OWNED BY public.app_user.id;


--
-- TOC entry 254 (class 1259 OID 17844)
-- Name: plugin_registry; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.plugin_registry (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    version character varying(50) NOT NULL,
    is_installed boolean DEFAULT true NOT NULL,
    installed_at timestamp with time zone NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.plugin_registry OWNER TO postgres;

--
-- TOC entry 5118 (class 0 OID 0)
-- Dependencies: 254
-- Name: TABLE plugin_registry; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.plugin_registry IS '
    插件注册表
    记录已安装的插件及其版本
    ';


--
-- TOC entry 5119 (class 0 OID 0)
-- Dependencies: 254
-- Name: COLUMN plugin_registry.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.plugin_registry.id IS '雪花算法主键 ID';


--
-- TOC entry 5120 (class 0 OID 0)
-- Dependencies: 254
-- Name: COLUMN plugin_registry.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.plugin_registry.name IS '插件名称';


--
-- TOC entry 5121 (class 0 OID 0)
-- Dependencies: 254
-- Name: COLUMN plugin_registry.version; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.plugin_registry.version IS '插件版本';


--
-- TOC entry 5122 (class 0 OID 0)
-- Dependencies: 254
-- Name: COLUMN plugin_registry.is_installed; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.plugin_registry.is_installed IS '是否已安装';


--
-- TOC entry 5123 (class 0 OID 0)
-- Dependencies: 254
-- Name: COLUMN plugin_registry.installed_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.plugin_registry.installed_at IS '安装时间';


--
-- TOC entry 5124 (class 0 OID 0)
-- Dependencies: 254
-- Name: COLUMN plugin_registry.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.plugin_registry.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5125 (class 0 OID 0)
-- Dependencies: 254
-- Name: COLUMN plugin_registry.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.plugin_registry.created_at IS '创建时间';


--
-- TOC entry 5126 (class 0 OID 0)
-- Dependencies: 254
-- Name: COLUMN plugin_registry.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.plugin_registry.updated_at IS '更新时间';


--
-- TOC entry 221 (class 1259 OID 16922)
-- Name: sys_config; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_config (
    id bigint NOT NULL,
    key character varying(100) NOT NULL,
    value character varying(255) NOT NULL,
    default_value character varying(255),
    validation_rule character varying(255),
    description character varying(255),
    type public.configtype NOT NULL,
    "group" public.configgroup NOT NULL,
    is_system boolean NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.sys_config OWNER TO postgres;

--
-- TOC entry 5127 (class 0 OID 0)
-- Dependencies: 221
-- Name: TABLE sys_config; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_config IS '
    系统配置表
    存储系统全局配置参数
    ';


--
-- TOC entry 5128 (class 0 OID 0)
-- Dependencies: 221
-- Name: COLUMN sys_config.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_config.id IS '雪花算法主键 ID';


--
-- TOC entry 5129 (class 0 OID 0)
-- Dependencies: 221
-- Name: COLUMN sys_config.key; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_config.key IS '配置键名';


--
-- TOC entry 5130 (class 0 OID 0)
-- Dependencies: 221
-- Name: COLUMN sys_config.value; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_config.value IS '配置值';


--
-- TOC entry 5131 (class 0 OID 0)
-- Dependencies: 221
-- Name: COLUMN sys_config.default_value; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_config.default_value IS '默认值';


--
-- TOC entry 5132 (class 0 OID 0)
-- Dependencies: 221
-- Name: COLUMN sys_config.validation_rule; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_config.validation_rule IS '校验规则';


--
-- TOC entry 5133 (class 0 OID 0)
-- Dependencies: 221
-- Name: COLUMN sys_config.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_config.description IS '配置描述';


--
-- TOC entry 5134 (class 0 OID 0)
-- Dependencies: 221
-- Name: COLUMN sys_config.type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_config.type IS '配置类型';


--
-- TOC entry 5135 (class 0 OID 0)
-- Dependencies: 221
-- Name: COLUMN sys_config."group"; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_config."group" IS '配置分组';


--
-- TOC entry 5136 (class 0 OID 0)
-- Dependencies: 221
-- Name: COLUMN sys_config.is_system; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_config.is_system IS '是否为系统内置配置';


--
-- TOC entry 5137 (class 0 OID 0)
-- Dependencies: 221
-- Name: COLUMN sys_config.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_config.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5138 (class 0 OID 0)
-- Dependencies: 221
-- Name: COLUMN sys_config.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_config.created_at IS '创建时间';


--
-- TOC entry 5139 (class 0 OID 0)
-- Dependencies: 221
-- Name: COLUMN sys_config.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_config.updated_at IS '更新时间';


--
-- TOC entry 220 (class 1259 OID 16921)
-- Name: sys_config_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sys_config_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sys_config_id_seq OWNER TO postgres;

--
-- TOC entry 5140 (class 0 OID 0)
-- Dependencies: 220
-- Name: sys_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sys_config_id_seq OWNED BY public.sys_config.id;


--
-- TOC entry 223 (class 1259 OID 16933)
-- Name: sys_dict; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_dict (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(100) NOT NULL,
    description text,
    status boolean NOT NULL,
    is_system boolean NOT NULL,
    sort integer NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.sys_dict OWNER TO postgres;

--
-- TOC entry 5141 (class 0 OID 0)
-- Dependencies: 223
-- Name: TABLE sys_dict; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_dict IS '
    系统字典表
    存储字典分类信息
    ';


--
-- TOC entry 5142 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN sys_dict.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict.id IS '雪花算法主键 ID';


--
-- TOC entry 5143 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN sys_dict.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict.name IS '字典名称';


--
-- TOC entry 5144 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN sys_dict.code; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict.code IS '字典编码';


--
-- TOC entry 5145 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN sys_dict.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict.description IS '字典描述';


--
-- TOC entry 5146 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN sys_dict.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict.status IS '状态：True-启用，False-禁用';


--
-- TOC entry 5147 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN sys_dict.is_system; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict.is_system IS '是否为系统内置字典';


--
-- TOC entry 5148 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN sys_dict.sort; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict.sort IS '排序号';


--
-- TOC entry 5149 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN sys_dict.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5150 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN sys_dict.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict.created_at IS '创建时间';


--
-- TOC entry 5151 (class 0 OID 0)
-- Dependencies: 223
-- Name: COLUMN sys_dict.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict.updated_at IS '更新时间';


--
-- TOC entry 222 (class 1259 OID 16932)
-- Name: sys_dict_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sys_dict_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sys_dict_id_seq OWNER TO postgres;

--
-- TOC entry 5152 (class 0 OID 0)
-- Dependencies: 222
-- Name: sys_dict_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sys_dict_id_seq OWNED BY public.sys_dict.id;


--
-- TOC entry 231 (class 1259 OID 17008)
-- Name: sys_dict_item; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_dict_item (
    id bigint NOT NULL,
    dict_id bigint NOT NULL,
    value character varying(100) NOT NULL,
    label character varying(100) NOT NULL,
    description text,
    ext_info text,
    status boolean NOT NULL,
    sort integer NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.sys_dict_item OWNER TO postgres;

--
-- TOC entry 5153 (class 0 OID 0)
-- Dependencies: 231
-- Name: TABLE sys_dict_item; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_dict_item IS '
    系统字典数据表
    存储字典的具体数据项
    ';


--
-- TOC entry 5154 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN sys_dict_item.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict_item.id IS '雪花算法主键 ID';


--
-- TOC entry 5155 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN sys_dict_item.dict_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict_item.dict_id IS '关联字典ID，字典删除时级联删除';


--
-- TOC entry 5156 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN sys_dict_item.value; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict_item.value IS '字典项值';


--
-- TOC entry 5157 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN sys_dict_item.label; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict_item.label IS '字典项文本';


--
-- TOC entry 5158 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN sys_dict_item.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict_item.description IS '字典项描述';


--
-- TOC entry 5159 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN sys_dict_item.ext_info; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict_item.ext_info IS '扩展信息(JSON格式)';


--
-- TOC entry 5160 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN sys_dict_item.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict_item.status IS '状态：True-启用，False-禁用';


--
-- TOC entry 5161 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN sys_dict_item.sort; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict_item.sort IS '排序号';


--
-- TOC entry 5162 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN sys_dict_item.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict_item.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5163 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN sys_dict_item.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict_item.created_at IS '创建时间';


--
-- TOC entry 5164 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN sys_dict_item.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_dict_item.updated_at IS '更新时间';


--
-- TOC entry 230 (class 1259 OID 17007)
-- Name: sys_dict_item_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sys_dict_item_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sys_dict_item_id_seq OWNER TO postgres;

--
-- TOC entry 5165 (class 0 OID 0)
-- Dependencies: 230
-- Name: sys_dict_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sys_dict_item_id_seq OWNED BY public.sys_dict_item.id;


--
-- TOC entry 237 (class 1259 OID 17066)
-- Name: sys_export_task; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_export_task (
    id bigint NOT NULL,
    task_name character varying(200) NOT NULL,
    module_key character varying(50) NOT NULL,
    template_id bigint,
    query_params_json text NOT NULL,
    created_by bigint NOT NULL,
    status character varying(20) NOT NULL,
    total_rows integer,
    file_path character varying(500),
    file_size integer,
    error_message text,
    started_at timestamp with time zone,
    finished_at timestamp with time zone,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.sys_export_task OWNER TO postgres;

--
-- TOC entry 5166 (class 0 OID 0)
-- Dependencies: 237
-- Name: TABLE sys_export_task; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_export_task IS '异步导出任务表';


--
-- TOC entry 5167 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN sys_export_task.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_task.id IS '雪花算法主键 ID';


--
-- TOC entry 5168 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN sys_export_task.task_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_task.task_name IS '任务名称';


--
-- TOC entry 5169 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN sys_export_task.module_key; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_task.module_key IS '模块标识';


--
-- TOC entry 5170 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN sys_export_task.template_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_task.template_id IS '导出模板ID';


--
-- TOC entry 5171 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN sys_export_task.query_params_json; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_task.query_params_json IS '查询参数JSON';


--
-- TOC entry 5172 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN sys_export_task.created_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_task.created_by IS '创建者ID';


--
-- TOC entry 5173 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN sys_export_task.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_task.status IS '状态: pending/processing/completed/failed';


--
-- TOC entry 5174 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN sys_export_task.total_rows; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_task.total_rows IS '导出总行数';


--
-- TOC entry 5175 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN sys_export_task.file_path; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_task.file_path IS '文件存储路径';


--
-- TOC entry 5176 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN sys_export_task.file_size; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_task.file_size IS '文件大小(字节)';


--
-- TOC entry 5177 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN sys_export_task.error_message; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_task.error_message IS '错误信息';


--
-- TOC entry 5178 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN sys_export_task.started_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_task.started_at IS '开始执行时间';


--
-- TOC entry 5179 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN sys_export_task.finished_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_task.finished_at IS '执行完成时间';


--
-- TOC entry 5180 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN sys_export_task.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_task.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5181 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN sys_export_task.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_task.created_at IS '创建时间';


--
-- TOC entry 5182 (class 0 OID 0)
-- Dependencies: 237
-- Name: COLUMN sys_export_task.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_task.updated_at IS '更新时间';


--
-- TOC entry 236 (class 1259 OID 17065)
-- Name: sys_export_task_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sys_export_task_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sys_export_task_id_seq OWNER TO postgres;

--
-- TOC entry 5183 (class 0 OID 0)
-- Dependencies: 236
-- Name: sys_export_task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sys_export_task_id_seq OWNED BY public.sys_export_task.id;


--
-- TOC entry 239 (class 1259 OID 17077)
-- Name: sys_export_template; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_export_template (
    id bigint NOT NULL,
    name character varying(200) NOT NULL,
    module_key character varying(50) NOT NULL,
    columns text NOT NULL,
    joins_config text,
    description character varying(500),
    created_by bigint NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.sys_export_template OWNER TO postgres;

--
-- TOC entry 5184 (class 0 OID 0)
-- Dependencies: 239
-- Name: TABLE sys_export_template; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_export_template IS '导出模板表';


--
-- TOC entry 5185 (class 0 OID 0)
-- Dependencies: 239
-- Name: COLUMN sys_export_template.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_template.id IS '雪花算法主键 ID';


--
-- TOC entry 5186 (class 0 OID 0)
-- Dependencies: 239
-- Name: COLUMN sys_export_template.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_template.name IS '模板名称';


--
-- TOC entry 5187 (class 0 OID 0)
-- Dependencies: 239
-- Name: COLUMN sys_export_template.module_key; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_template.module_key IS '关联模块标识';


--
-- TOC entry 5188 (class 0 OID 0)
-- Dependencies: 239
-- Name: COLUMN sys_export_template.columns; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_template.columns IS '列配置JSON';


--
-- TOC entry 5189 (class 0 OID 0)
-- Dependencies: 239
-- Name: COLUMN sys_export_template.joins_config; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_template.joins_config IS 'JOIN配置JSON，为空则单表查询';


--
-- TOC entry 5190 (class 0 OID 0)
-- Dependencies: 239
-- Name: COLUMN sys_export_template.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_template.description IS '模板描述';


--
-- TOC entry 5191 (class 0 OID 0)
-- Dependencies: 239
-- Name: COLUMN sys_export_template.created_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_template.created_by IS '创建者ID';


--
-- TOC entry 5192 (class 0 OID 0)
-- Dependencies: 239
-- Name: COLUMN sys_export_template.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_template.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5193 (class 0 OID 0)
-- Dependencies: 239
-- Name: COLUMN sys_export_template.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_template.created_at IS '创建时间';


--
-- TOC entry 5194 (class 0 OID 0)
-- Dependencies: 239
-- Name: COLUMN sys_export_template.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_export_template.updated_at IS '更新时间';


--
-- TOC entry 238 (class 1259 OID 17076)
-- Name: sys_export_template_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sys_export_template_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sys_export_template_id_seq OWNER TO postgres;

--
-- TOC entry 5195 (class 0 OID 0)
-- Dependencies: 238
-- Name: sys_export_template_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sys_export_template_id_seq OWNED BY public.sys_export_template.id;


--
-- TOC entry 245 (class 1259 OID 17336)
-- Name: sys_file; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_file (
    id bigint NOT NULL,
    original_name character varying(500) NOT NULL,
    stored_name character varying(500) NOT NULL,
    file_path character varying(1000) NOT NULL,
    file_size bigint NOT NULL,
    mime_type character varying(200) NOT NULL,
    extension character varying(20) NOT NULL,
    created_by bigint NOT NULL,
    storage_platform character varying(50) NOT NULL,
    hash character varying(64),
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.sys_file OWNER TO postgres;

--
-- TOC entry 5196 (class 0 OID 0)
-- Dependencies: 245
-- Name: TABLE sys_file; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_file IS '
    系统文件存储表
    ';


--
-- TOC entry 5197 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN sys_file.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_file.id IS '雪花算法主键 ID';


--
-- TOC entry 5198 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN sys_file.original_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_file.original_name IS '原始文件名';


--
-- TOC entry 5199 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN sys_file.stored_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_file.stored_name IS '存储文件名';


--
-- TOC entry 5200 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN sys_file.file_path; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_file.file_path IS '存储路径';


--
-- TOC entry 5201 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN sys_file.file_size; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_file.file_size IS '文件大小(字节)';


--
-- TOC entry 5202 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN sys_file.mime_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_file.mime_type IS 'MIME类型';


--
-- TOC entry 5203 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN sys_file.extension; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_file.extension IS '扩展名';


--
-- TOC entry 5204 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN sys_file.created_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_file.created_by IS '上传者用户ID';


--
-- TOC entry 5205 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN sys_file.storage_platform; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_file.storage_platform IS '存储平台标识';


--
-- TOC entry 5206 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN sys_file.hash; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_file.hash IS 'SHA-256哈希';


--
-- TOC entry 5207 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN sys_file.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_file.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5208 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN sys_file.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_file.created_at IS '创建时间';


--
-- TOC entry 5209 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN sys_file.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_file.updated_at IS '更新时间';


--
-- TOC entry 244 (class 1259 OID 17335)
-- Name: sys_file_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sys_file_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sys_file_id_seq OWNER TO postgres;

--
-- TOC entry 5210 (class 0 OID 0)
-- Dependencies: 244
-- Name: sys_file_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sys_file_id_seq OWNED BY public.sys_file.id;


--
-- TOC entry 243 (class 1259 OID 17108)
-- Name: sys_ip_blacklist; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_ip_blacklist (
    id bigint NOT NULL,
    ip character varying(64) NOT NULL,
    type character varying(16) NOT NULL,
    reason character varying(255),
    expire_at timestamp with time zone,
    creator_id bigint,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.sys_ip_blacklist OWNER TO postgres;

--
-- TOC entry 5211 (class 0 OID 0)
-- Dependencies: 243
-- Name: TABLE sys_ip_blacklist; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_ip_blacklist IS '
    IP 黑名单表
    permanent: 永久；temporary: 临时（expire_at 为空表示永久）
    ';


--
-- TOC entry 5212 (class 0 OID 0)
-- Dependencies: 243
-- Name: COLUMN sys_ip_blacklist.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_ip_blacklist.id IS '雪花算法主键 ID';


--
-- TOC entry 5213 (class 0 OID 0)
-- Dependencies: 243
-- Name: COLUMN sys_ip_blacklist.ip; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_ip_blacklist.ip IS 'IP 地址';


--
-- TOC entry 5214 (class 0 OID 0)
-- Dependencies: 243
-- Name: COLUMN sys_ip_blacklist.type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_ip_blacklist.type IS '类型：permanent / temporary';


--
-- TOC entry 5215 (class 0 OID 0)
-- Dependencies: 243
-- Name: COLUMN sys_ip_blacklist.reason; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_ip_blacklist.reason IS '加入原因';


--
-- TOC entry 5216 (class 0 OID 0)
-- Dependencies: 243
-- Name: COLUMN sys_ip_blacklist.expire_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_ip_blacklist.expire_at IS '过期时间（temporary 必填）';


--
-- TOC entry 5217 (class 0 OID 0)
-- Dependencies: 243
-- Name: COLUMN sys_ip_blacklist.creator_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_ip_blacklist.creator_id IS '创建人ID（系统自动写入时为空）';


--
-- TOC entry 5218 (class 0 OID 0)
-- Dependencies: 243
-- Name: COLUMN sys_ip_blacklist.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_ip_blacklist.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5219 (class 0 OID 0)
-- Dependencies: 243
-- Name: COLUMN sys_ip_blacklist.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_ip_blacklist.created_at IS '创建时间';


--
-- TOC entry 5220 (class 0 OID 0)
-- Dependencies: 243
-- Name: COLUMN sys_ip_blacklist.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_ip_blacklist.updated_at IS '更新时间';


--
-- TOC entry 242 (class 1259 OID 17107)
-- Name: sys_ip_blacklist_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sys_ip_blacklist_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sys_ip_blacklist_id_seq OWNER TO postgres;

--
-- TOC entry 5221 (class 0 OID 0)
-- Dependencies: 242
-- Name: sys_ip_blacklist_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sys_ip_blacklist_id_seq OWNED BY public.sys_ip_blacklist.id;


--
-- TOC entry 241 (class 1259 OID 17088)
-- Name: sys_login_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_login_log (
    id bigint NOT NULL,
    username character varying(50) NOT NULL,
    ip character varying(50),
    status boolean NOT NULL,
    detail character varying(255),
    user_agent character varying(500),
    login_time timestamp with time zone NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.sys_login_log OWNER TO postgres;

--
-- TOC entry 5222 (class 0 OID 0)
-- Dependencies: 241
-- Name: TABLE sys_login_log; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_login_log IS '
    系统登录日志表
    记录用户登录尝试（成功和失败）
    ';


--
-- TOC entry 5223 (class 0 OID 0)
-- Dependencies: 241
-- Name: COLUMN sys_login_log.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_login_log.id IS '雪花算法主键 ID';


--
-- TOC entry 5224 (class 0 OID 0)
-- Dependencies: 241
-- Name: COLUMN sys_login_log.username; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_login_log.username IS '登录用户名';


--
-- TOC entry 5225 (class 0 OID 0)
-- Dependencies: 241
-- Name: COLUMN sys_login_log.ip; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_login_log.ip IS '客户端IP';


--
-- TOC entry 5226 (class 0 OID 0)
-- Dependencies: 241
-- Name: COLUMN sys_login_log.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_login_log.status IS '登录状态：True-成功，False-失败';


--
-- TOC entry 5227 (class 0 OID 0)
-- Dependencies: 241
-- Name: COLUMN sys_login_log.detail; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_login_log.detail IS '详情：登录成功/密码错误/用户不存在等';


--
-- TOC entry 5228 (class 0 OID 0)
-- Dependencies: 241
-- Name: COLUMN sys_login_log.user_agent; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_login_log.user_agent IS '登录设备(User-Agent)';


--
-- TOC entry 5229 (class 0 OID 0)
-- Dependencies: 241
-- Name: COLUMN sys_login_log.login_time; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_login_log.login_time IS '登录时间';


--
-- TOC entry 5230 (class 0 OID 0)
-- Dependencies: 241
-- Name: COLUMN sys_login_log.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_login_log.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5231 (class 0 OID 0)
-- Dependencies: 241
-- Name: COLUMN sys_login_log.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_login_log.created_at IS '创建时间';


--
-- TOC entry 5232 (class 0 OID 0)
-- Dependencies: 241
-- Name: COLUMN sys_login_log.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_login_log.updated_at IS '更新时间';


--
-- TOC entry 240 (class 1259 OID 17087)
-- Name: sys_login_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sys_login_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sys_login_log_id_seq OWNER TO postgres;

--
-- TOC entry 5233 (class 0 OID 0)
-- Dependencies: 240
-- Name: sys_login_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sys_login_log_id_seq OWNED BY public.sys_login_log.id;


--
-- TOC entry 225 (class 1259 OID 16954)
-- Name: sys_menu; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_menu (
    id bigint NOT NULL,
    parent_id bigint,
    name character varying(100) NOT NULL,
    path character varying(255),
    component character varying(255),
    redirect character varying(255),
    permission character varying(100),
    meta_icon character varying(50),
    meta_hidden boolean NOT NULL,
    meta_affix boolean NOT NULL,
    meta_breadcrumb boolean NOT NULL,
    status boolean NOT NULL,
    type public.menutype NOT NULL,
    sort integer NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone,
    is_system boolean NOT NULL,
    meta_href character varying(500),
    meta_keep_alive boolean NOT NULL
);


ALTER TABLE public.sys_menu OWNER TO postgres;

--
-- TOC entry 5234 (class 0 OID 0)
-- Dependencies: 225
-- Name: TABLE sys_menu; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_menu IS '
    系统菜单表
    存储系统菜单、目录和按钮等权限点
    ';


--
-- TOC entry 5235 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.id IS '雪花算法主键 ID';


--
-- TOC entry 5236 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.parent_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.parent_id IS '父菜单ID，顶级菜单为0或NULL';


--
-- TOC entry 5237 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.name IS '菜单名称';


--
-- TOC entry 5238 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.path; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.path IS '路由路径';


--
-- TOC entry 5239 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.component; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.component IS '组件路径';


--
-- TOC entry 5240 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.redirect; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.redirect IS '重定向路径';


--
-- TOC entry 5241 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.permission; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.permission IS '权限标识，如 sys:user:list';


--
-- TOC entry 5242 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.meta_icon; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.meta_icon IS '路由图标';


--
-- TOC entry 5243 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.meta_hidden; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.meta_hidden IS '是否隐藏菜单';


--
-- TOC entry 5244 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.meta_affix; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.meta_affix IS '是否固定标签';


--
-- TOC entry 5245 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.meta_breadcrumb; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.meta_breadcrumb IS '是否显示面包屑';


--
-- TOC entry 5246 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.status IS '状态：True-启用，False-禁用';


--
-- TOC entry 5247 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.type IS '菜单类型：catalog-目录, menu-菜单, button-按钮, external-外部链接';


--
-- TOC entry 5248 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.sort; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.sort IS '排序号';


--
-- TOC entry 5249 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5250 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.created_at IS '创建时间';


--
-- TOC entry 5251 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.updated_at IS '更新时间';


--
-- TOC entry 5252 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.is_system; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.is_system IS '是否为系统内置菜单';


--
-- TOC entry 5253 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.meta_href; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.meta_href IS '外部链接地址';


--
-- TOC entry 5254 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN sys_menu.meta_keep_alive; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_menu.meta_keep_alive IS '是否缓存路由';


--
-- TOC entry 224 (class 1259 OID 16953)
-- Name: sys_menu_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sys_menu_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sys_menu_id_seq OWNER TO postgres;

--
-- TOC entry 5255 (class 0 OID 0)
-- Dependencies: 224
-- Name: sys_menu_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sys_menu_id_seq OWNED BY public.sys_menu.id;


--
-- TOC entry 247 (class 1259 OID 17404)
-- Name: sys_notice; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_notice (
    id bigint NOT NULL,
    title character varying(200) NOT NULL,
    content text NOT NULL,
    sender_id bigint NOT NULL,
    sender_name character varying(100) NOT NULL,
    type character varying(50) NOT NULL,
    target_type character varying(50) NOT NULL,
    target_role_ids bigint[],
    target_user_ids bigint[],
    priority character varying(20) NOT NULL,
    status boolean NOT NULL,
    published_at timestamp with time zone,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.sys_notice OWNER TO postgres;

--
-- TOC entry 5256 (class 0 OID 0)
-- Dependencies: 247
-- Name: TABLE sys_notice; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_notice IS '
    系统通知表
    存储系统公告、操作提醒、审批通知等
    ';


--
-- TOC entry 5257 (class 0 OID 0)
-- Dependencies: 247
-- Name: COLUMN sys_notice.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice.id IS '雪花算法主键 ID';


--
-- TOC entry 5258 (class 0 OID 0)
-- Dependencies: 247
-- Name: COLUMN sys_notice.title; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice.title IS '通知标题';


--
-- TOC entry 5259 (class 0 OID 0)
-- Dependencies: 247
-- Name: COLUMN sys_notice.content; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice.content IS '通知内容（支持HTML）';


--
-- TOC entry 5260 (class 0 OID 0)
-- Dependencies: 247
-- Name: COLUMN sys_notice.sender_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice.sender_id IS '发送者用户ID';


--
-- TOC entry 5261 (class 0 OID 0)
-- Dependencies: 247
-- Name: COLUMN sys_notice.sender_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice.sender_name IS '发送者名称';


--
-- TOC entry 5262 (class 0 OID 0)
-- Dependencies: 247
-- Name: COLUMN sys_notice.type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice.type IS '通知类型：announcement-公告, system-系统, operation-操作提醒, approval-审批通知';


--
-- TOC entry 5263 (class 0 OID 0)
-- Dependencies: 247
-- Name: COLUMN sys_notice.target_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice.target_type IS '推送范围：all-全员, role-按角色, user-按指定用户';


--
-- TOC entry 5264 (class 0 OID 0)
-- Dependencies: 247
-- Name: COLUMN sys_notice.target_role_ids; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice.target_role_ids IS '目标角色ID列表（target_type=role时有效）';


--
-- TOC entry 5265 (class 0 OID 0)
-- Dependencies: 247
-- Name: COLUMN sys_notice.target_user_ids; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice.target_user_ids IS '目标用户ID列表（target_type=user时有效）';


--
-- TOC entry 5266 (class 0 OID 0)
-- Dependencies: 247
-- Name: COLUMN sys_notice.priority; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice.priority IS '优先级：low-低, normal-普通, high-高, urgent-紧急';


--
-- TOC entry 5267 (class 0 OID 0)
-- Dependencies: 247
-- Name: COLUMN sys_notice.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice.status IS '状态：True-已发布, False-草稿';


--
-- TOC entry 5268 (class 0 OID 0)
-- Dependencies: 247
-- Name: COLUMN sys_notice.published_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice.published_at IS '发布时间';


--
-- TOC entry 5269 (class 0 OID 0)
-- Dependencies: 247
-- Name: COLUMN sys_notice.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5270 (class 0 OID 0)
-- Dependencies: 247
-- Name: COLUMN sys_notice.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice.created_at IS '创建时间';


--
-- TOC entry 5271 (class 0 OID 0)
-- Dependencies: 247
-- Name: COLUMN sys_notice.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice.updated_at IS '更新时间';


--
-- TOC entry 246 (class 1259 OID 17403)
-- Name: sys_notice_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sys_notice_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sys_notice_id_seq OWNER TO postgres;

--
-- TOC entry 5272 (class 0 OID 0)
-- Dependencies: 246
-- Name: sys_notice_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sys_notice_id_seq OWNED BY public.sys_notice.id;


--
-- TOC entry 249 (class 1259 OID 17414)
-- Name: sys_notice_read; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_notice_read (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    notice_id bigint NOT NULL,
    is_read boolean NOT NULL,
    read_at timestamp with time zone,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.sys_notice_read OWNER TO postgres;

--
-- TOC entry 5273 (class 0 OID 0)
-- Dependencies: 249
-- Name: TABLE sys_notice_read; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_notice_read IS '用户通知阅读记录表';


--
-- TOC entry 5274 (class 0 OID 0)
-- Dependencies: 249
-- Name: COLUMN sys_notice_read.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice_read.id IS '雪花算法主键 ID';


--
-- TOC entry 5275 (class 0 OID 0)
-- Dependencies: 249
-- Name: COLUMN sys_notice_read.user_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice_read.user_id IS '用户ID';


--
-- TOC entry 5276 (class 0 OID 0)
-- Dependencies: 249
-- Name: COLUMN sys_notice_read.notice_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice_read.notice_id IS '通知ID';


--
-- TOC entry 5277 (class 0 OID 0)
-- Dependencies: 249
-- Name: COLUMN sys_notice_read.is_read; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice_read.is_read IS '是否已读';


--
-- TOC entry 5278 (class 0 OID 0)
-- Dependencies: 249
-- Name: COLUMN sys_notice_read.read_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice_read.read_at IS '阅读时间';


--
-- TOC entry 5279 (class 0 OID 0)
-- Dependencies: 249
-- Name: COLUMN sys_notice_read.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice_read.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5280 (class 0 OID 0)
-- Dependencies: 249
-- Name: COLUMN sys_notice_read.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice_read.created_at IS '创建时间';


--
-- TOC entry 5281 (class 0 OID 0)
-- Dependencies: 249
-- Name: COLUMN sys_notice_read.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_notice_read.updated_at IS '更新时间';


--
-- TOC entry 248 (class 1259 OID 17413)
-- Name: sys_notice_read_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sys_notice_read_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sys_notice_read_id_seq OWNER TO postgres;

--
-- TOC entry 5282 (class 0 OID 0)
-- Dependencies: 248
-- Name: sys_notice_read_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sys_notice_read_id_seq OWNED BY public.sys_notice_read.id;


--
-- TOC entry 235 (class 1259 OID 17055)
-- Name: sys_operation_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_operation_log (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    username character varying(50) NOT NULL,
    module character varying(50) NOT NULL,
    action character varying(50) NOT NULL,
    description character varying(255),
    method character varying(10),
    path character varying(255),
    ip character varying(50),
    request_params text,
    response_code integer,
    elapsed_ms double precision,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone,
    response_result text
);


ALTER TABLE public.sys_operation_log OWNER TO postgres;

--
-- TOC entry 5283 (class 0 OID 0)
-- Dependencies: 235
-- Name: TABLE sys_operation_log; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_operation_log IS '
    系统操作日志表
    记录用户的关键业务操作
    ';


--
-- TOC entry 5284 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN sys_operation_log.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_operation_log.id IS '雪花算法主键 ID';


--
-- TOC entry 5285 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN sys_operation_log.user_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_operation_log.user_id IS '操作人ID';


--
-- TOC entry 5286 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN sys_operation_log.username; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_operation_log.username IS '操作人用户名';


--
-- TOC entry 5287 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN sys_operation_log.module; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_operation_log.module IS '操作模块';


--
-- TOC entry 5288 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN sys_operation_log.action; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_operation_log.action IS '操作类型';


--
-- TOC entry 5289 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN sys_operation_log.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_operation_log.description IS '操作描述';


--
-- TOC entry 5290 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN sys_operation_log.method; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_operation_log.method IS 'HTTP方法';


--
-- TOC entry 5291 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN sys_operation_log.path; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_operation_log.path IS '请求路径';


--
-- TOC entry 5292 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN sys_operation_log.ip; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_operation_log.ip IS '客户端IP';


--
-- TOC entry 5293 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN sys_operation_log.request_params; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_operation_log.request_params IS '请求参数';


--
-- TOC entry 5294 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN sys_operation_log.response_code; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_operation_log.response_code IS '响应状态码';


--
-- TOC entry 5295 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN sys_operation_log.elapsed_ms; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_operation_log.elapsed_ms IS '耗时(毫秒)';


--
-- TOC entry 5296 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN sys_operation_log.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_operation_log.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5297 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN sys_operation_log.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_operation_log.created_at IS '创建时间';


--
-- TOC entry 5298 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN sys_operation_log.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_operation_log.updated_at IS '更新时间';


--
-- TOC entry 5299 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN sys_operation_log.response_result; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_operation_log.response_result IS '响应结果';


--
-- TOC entry 234 (class 1259 OID 17054)
-- Name: sys_operation_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sys_operation_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sys_operation_log_id_seq OWNER TO postgres;

--
-- TOC entry 5300 (class 0 OID 0)
-- Dependencies: 234
-- Name: sys_operation_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sys_operation_log_id_seq OWNED BY public.sys_operation_log.id;


--
-- TOC entry 227 (class 1259 OID 16980)
-- Name: sys_role; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_role (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    status boolean NOT NULL,
    is_default boolean NOT NULL,
    is_system boolean NOT NULL,
    sort integer NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone,
    "desc" text
);


ALTER TABLE public.sys_role OWNER TO postgres;

--
-- TOC entry 5301 (class 0 OID 0)
-- Dependencies: 227
-- Name: TABLE sys_role; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_role IS '
    系统角色表
    存储角色信息及其关联的权限配置
    ';


--
-- TOC entry 5302 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN sys_role.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_role.id IS '雪花算法主键 ID';


--
-- TOC entry 5303 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN sys_role.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_role.name IS '角色名称';


--
-- TOC entry 5304 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN sys_role.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_role.status IS '状态：True-启用，False-禁用';


--
-- TOC entry 5305 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN sys_role.is_default; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_role.is_default IS '是否为默认角色';


--
-- TOC entry 5306 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN sys_role.is_system; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_role.is_system IS '是否为系统内置角色';


--
-- TOC entry 5307 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN sys_role.sort; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_role.sort IS '排序号';


--
-- TOC entry 5308 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN sys_role.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_role.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5309 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN sys_role.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_role.created_at IS '创建时间';


--
-- TOC entry 5310 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN sys_role.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_role.updated_at IS '更新时间';


--
-- TOC entry 5311 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN sys_role."desc"; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_role."desc" IS '角色描述';


--
-- TOC entry 226 (class 1259 OID 16979)
-- Name: sys_role_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sys_role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sys_role_id_seq OWNER TO postgres;

--
-- TOC entry 5312 (class 0 OID 0)
-- Dependencies: 226
-- Name: sys_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sys_role_id_seq OWNED BY public.sys_role.id;


--
-- TOC entry 232 (class 1259 OID 17022)
-- Name: sys_role_menu; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_role_menu (
    role_id bigint NOT NULL,
    menu_id bigint NOT NULL,
    permission character varying(255) NOT NULL
);


ALTER TABLE public.sys_role_menu OWNER TO postgres;

--
-- TOC entry 5313 (class 0 OID 0)
-- Dependencies: 232
-- Name: TABLE sys_role_menu; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_role_menu IS '角色菜单关联表';


--
-- TOC entry 5314 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN sys_role_menu.role_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_role_menu.role_id IS '角色ID';


--
-- TOC entry 5315 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN sys_role_menu.menu_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_role_menu.menu_id IS '菜单ID';


--
-- TOC entry 5316 (class 0 OID 0)
-- Dependencies: 232
-- Name: COLUMN sys_role_menu.permission; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_role_menu.permission IS '权限类型：read, write, delete等';


--
-- TOC entry 251 (class 1259 OID 17812)
-- Name: sys_scheduled_task; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_scheduled_task (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    task_key character varying(200) NOT NULL,
    cron_expression character varying(100) NOT NULL,
    description character varying(500),
    trigger_type character varying(20) NOT NULL,
    trigger_params text,
    status boolean NOT NULL,
    module character varying(100),
    function_path character varying(200),
    is_system boolean NOT NULL,
    last_run_at timestamp with time zone,
    next_run_at timestamp with time zone,
    last_status character varying(20),
    timeout integer NOT NULL,
    max_retries integer NOT NULL,
    concurrent_policy character varying(20) NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.sys_scheduled_task OWNER TO postgres;

--
-- TOC entry 5317 (class 0 OID 0)
-- Dependencies: 251
-- Name: TABLE sys_scheduled_task; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_scheduled_task IS '定时任务表';


--
-- TOC entry 5318 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.id IS '雪花算法主键 ID';


--
-- TOC entry 5319 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.name IS '任务名称';


--
-- TOC entry 5320 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.task_key; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.task_key IS '任务唯一标识';


--
-- TOC entry 5321 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.cron_expression; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.cron_expression IS 'Cron 表达式';


--
-- TOC entry 5322 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.description IS '任务描述';


--
-- TOC entry 5323 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.trigger_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.trigger_type IS '触发类型: cron/interval/date';


--
-- TOC entry 5324 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.trigger_params; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.trigger_params IS '触发参数 JSON';


--
-- TOC entry 5325 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.status IS '状态: True启用/False禁用';


--
-- TOC entry 5326 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.module; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.module IS '来源模块';


--
-- TOC entry 5327 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.function_path; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.function_path IS '函数路径';


--
-- TOC entry 5328 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.is_system; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.is_system IS '系统任务不可删除';


--
-- TOC entry 5329 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.last_run_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.last_run_at IS '上次执行时间';


--
-- TOC entry 5330 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.next_run_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.next_run_at IS '下次执行时间';


--
-- TOC entry 5331 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.last_status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.last_status IS '上次执行状态: success/failed/running';


--
-- TOC entry 5332 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.timeout; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.timeout IS '超时时间(秒)';


--
-- TOC entry 5333 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.max_retries; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.max_retries IS '最大重试次数';


--
-- TOC entry 5334 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.concurrent_policy; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.concurrent_policy IS '并发策略: skip/replace/run';


--
-- TOC entry 5335 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5336 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.created_at IS '创建时间';


--
-- TOC entry 5337 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN sys_scheduled_task.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task.updated_at IS '更新时间';


--
-- TOC entry 250 (class 1259 OID 17811)
-- Name: sys_scheduled_task_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sys_scheduled_task_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sys_scheduled_task_id_seq OWNER TO postgres;

--
-- TOC entry 5338 (class 0 OID 0)
-- Dependencies: 250
-- Name: sys_scheduled_task_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sys_scheduled_task_id_seq OWNED BY public.sys_scheduled_task.id;


--
-- TOC entry 253 (class 1259 OID 17823)
-- Name: sys_scheduled_task_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_scheduled_task_log (
    id bigint NOT NULL,
    task_id bigint NOT NULL,
    task_name character varying(100) NOT NULL,
    task_key character varying(200) NOT NULL,
    status character varying(20) NOT NULL,
    start_time timestamp with time zone,
    end_time timestamp with time zone,
    duration_ms double precision,
    result text,
    error_message text,
    retry_count integer NOT NULL,
    triggered_by character varying(20) NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.sys_scheduled_task_log OWNER TO postgres;

--
-- TOC entry 5339 (class 0 OID 0)
-- Dependencies: 253
-- Name: TABLE sys_scheduled_task_log; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_scheduled_task_log IS '定时任务执行日志表';


--
-- TOC entry 5340 (class 0 OID 0)
-- Dependencies: 253
-- Name: COLUMN sys_scheduled_task_log.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task_log.id IS '雪花算法主键 ID';


--
-- TOC entry 5341 (class 0 OID 0)
-- Dependencies: 253
-- Name: COLUMN sys_scheduled_task_log.task_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task_log.task_id IS '任务ID';


--
-- TOC entry 5342 (class 0 OID 0)
-- Dependencies: 253
-- Name: COLUMN sys_scheduled_task_log.task_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task_log.task_name IS '任务名称(冗余)';


--
-- TOC entry 5343 (class 0 OID 0)
-- Dependencies: 253
-- Name: COLUMN sys_scheduled_task_log.task_key; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task_log.task_key IS '任务标识(冗余)';


--
-- TOC entry 5344 (class 0 OID 0)
-- Dependencies: 253
-- Name: COLUMN sys_scheduled_task_log.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task_log.status IS '状态: running/success/failed/timeout';


--
-- TOC entry 5345 (class 0 OID 0)
-- Dependencies: 253
-- Name: COLUMN sys_scheduled_task_log.start_time; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task_log.start_time IS '开始时间';


--
-- TOC entry 5346 (class 0 OID 0)
-- Dependencies: 253
-- Name: COLUMN sys_scheduled_task_log.end_time; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task_log.end_time IS '结束时间';


--
-- TOC entry 5347 (class 0 OID 0)
-- Dependencies: 253
-- Name: COLUMN sys_scheduled_task_log.duration_ms; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task_log.duration_ms IS '耗时(毫秒)';


--
-- TOC entry 5348 (class 0 OID 0)
-- Dependencies: 253
-- Name: COLUMN sys_scheduled_task_log.result; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task_log.result IS '执行结果';


--
-- TOC entry 5349 (class 0 OID 0)
-- Dependencies: 253
-- Name: COLUMN sys_scheduled_task_log.error_message; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task_log.error_message IS '错误信息';


--
-- TOC entry 5350 (class 0 OID 0)
-- Dependencies: 253
-- Name: COLUMN sys_scheduled_task_log.retry_count; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task_log.retry_count IS '重试次数';


--
-- TOC entry 5351 (class 0 OID 0)
-- Dependencies: 253
-- Name: COLUMN sys_scheduled_task_log.triggered_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task_log.triggered_by IS '触发方式: scheduler/manual';


--
-- TOC entry 5352 (class 0 OID 0)
-- Dependencies: 253
-- Name: COLUMN sys_scheduled_task_log.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task_log.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5353 (class 0 OID 0)
-- Dependencies: 253
-- Name: COLUMN sys_scheduled_task_log.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task_log.created_at IS '创建时间';


--
-- TOC entry 5354 (class 0 OID 0)
-- Dependencies: 253
-- Name: COLUMN sys_scheduled_task_log.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_scheduled_task_log.updated_at IS '更新时间';


--
-- TOC entry 252 (class 1259 OID 17822)
-- Name: sys_scheduled_task_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sys_scheduled_task_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sys_scheduled_task_log_id_seq OWNER TO postgres;

--
-- TOC entry 5355 (class 0 OID 0)
-- Dependencies: 252
-- Name: sys_scheduled_task_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sys_scheduled_task_log_id_seq OWNED BY public.sys_scheduled_task_log.id;


--
-- TOC entry 229 (class 1259 OID 16993)
-- Name: sys_user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_user (
    id bigint NOT NULL,
    username character varying(50) NOT NULL,
    password character varying(255) NOT NULL,
    nickname character varying(100),
    email character varying(100),
    phone character varying(20),
    avatar text,
    last_login_at timestamp with time zone,
    last_login_ip character varying(50),
    status boolean NOT NULL,
    is_superuser boolean NOT NULL,
    deleted_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone,
    last_tenant_id bigint
);


ALTER TABLE public.sys_user OWNER TO postgres;

--
-- TOC entry 5356 (class 0 OID 0)
-- Dependencies: 229
-- Name: TABLE sys_user; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_user IS '
    系统用户表
    存储系统管理用户的基本信息和认证凭证
    ';


--
-- TOC entry 5357 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN sys_user.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user.id IS '雪花算法主键 ID';


--
-- TOC entry 5358 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN sys_user.username; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user.username IS '用户名';


--
-- TOC entry 5359 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN sys_user.password; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user.password IS '密码（bcrypt加密存储）';


--
-- TOC entry 5360 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN sys_user.nickname; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user.nickname IS '用户昵称';


--
-- TOC entry 5361 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN sys_user.email; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user.email IS '邮箱';


--
-- TOC entry 5362 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN sys_user.phone; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user.phone IS '手机号';


--
-- TOC entry 5363 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN sys_user.avatar; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user.avatar IS '头像URL';


--
-- TOC entry 5364 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN sys_user.last_login_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user.last_login_at IS '最后登录时间';


--
-- TOC entry 5365 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN sys_user.last_login_ip; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user.last_login_ip IS '最后登录IP';


--
-- TOC entry 5366 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN sys_user.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user.status IS '状态：True-启用，False-禁用';


--
-- TOC entry 5367 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN sys_user.is_superuser; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user.is_superuser IS '是否为超级管理员';


--
-- TOC entry 5368 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN sys_user.deleted_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user.deleted_at IS '删除时间，为空则未删除';


--
-- TOC entry 5369 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN sys_user.created_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user.created_at IS '创建时间';


--
-- TOC entry 5370 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN sys_user.updated_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user.updated_at IS '更新时间';


--
-- TOC entry 5371 (class 0 OID 0)
-- Dependencies: 229
-- Name: COLUMN sys_user.last_tenant_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user.last_tenant_id IS '最后选择的租户ID';


--
-- TOC entry 228 (class 1259 OID 16992)
-- Name: sys_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sys_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sys_user_id_seq OWNER TO postgres;

--
-- TOC entry 5372 (class 0 OID 0)
-- Dependencies: 228
-- Name: sys_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sys_user_id_seq OWNED BY public.sys_user.id;


--
-- TOC entry 233 (class 1259 OID 17037)
-- Name: sys_user_role; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sys_user_role (
    user_id bigint NOT NULL,
    role_id bigint NOT NULL
);


ALTER TABLE public.sys_user_role OWNER TO postgres;

--
-- TOC entry 5373 (class 0 OID 0)
-- Dependencies: 233
-- Name: TABLE sys_user_role; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.sys_user_role IS '用户角色关联表';


--
-- TOC entry 5374 (class 0 OID 0)
-- Dependencies: 233
-- Name: COLUMN sys_user_role.user_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user_role.user_id IS '用户ID';


--
-- TOC entry 5375 (class 0 OID 0)
-- Dependencies: 233
-- Name: COLUMN sys_user_role.role_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sys_user_role.role_id IS '角色ID';


--
-- TOC entry 4815 (class 2604 OID 16890)
-- Name: app_user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user ALTER COLUMN id SET DEFAULT nextval('public.app_user_id_seq'::regclass);


--
-- TOC entry 4816 (class 2604 OID 16925)
-- Name: sys_config id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_config ALTER COLUMN id SET DEFAULT nextval('public.sys_config_id_seq'::regclass);


--
-- TOC entry 4817 (class 2604 OID 16936)
-- Name: sys_dict id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_dict ALTER COLUMN id SET DEFAULT nextval('public.sys_dict_id_seq'::regclass);


--
-- TOC entry 4821 (class 2604 OID 17011)
-- Name: sys_dict_item id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_dict_item ALTER COLUMN id SET DEFAULT nextval('public.sys_dict_item_id_seq'::regclass);


--
-- TOC entry 4823 (class 2604 OID 17069)
-- Name: sys_export_task id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_export_task ALTER COLUMN id SET DEFAULT nextval('public.sys_export_task_id_seq'::regclass);


--
-- TOC entry 4824 (class 2604 OID 17080)
-- Name: sys_export_template id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_export_template ALTER COLUMN id SET DEFAULT nextval('public.sys_export_template_id_seq'::regclass);


--
-- TOC entry 4828 (class 2604 OID 17339)
-- Name: sys_file id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_file ALTER COLUMN id SET DEFAULT nextval('public.sys_file_id_seq'::regclass);


--
-- TOC entry 4826 (class 2604 OID 17111)
-- Name: sys_ip_blacklist id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_ip_blacklist ALTER COLUMN id SET DEFAULT nextval('public.sys_ip_blacklist_id_seq'::regclass);


--
-- TOC entry 4825 (class 2604 OID 17091)
-- Name: sys_login_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_login_log ALTER COLUMN id SET DEFAULT nextval('public.sys_login_log_id_seq'::regclass);


--
-- TOC entry 4818 (class 2604 OID 16957)
-- Name: sys_menu id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_menu ALTER COLUMN id SET DEFAULT nextval('public.sys_menu_id_seq'::regclass);


--
-- TOC entry 4829 (class 2604 OID 17407)
-- Name: sys_notice id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_notice ALTER COLUMN id SET DEFAULT nextval('public.sys_notice_id_seq'::regclass);


--
-- TOC entry 4830 (class 2604 OID 17417)
-- Name: sys_notice_read id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_notice_read ALTER COLUMN id SET DEFAULT nextval('public.sys_notice_read_id_seq'::regclass);


--
-- TOC entry 4822 (class 2604 OID 17058)
-- Name: sys_operation_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_operation_log ALTER COLUMN id SET DEFAULT nextval('public.sys_operation_log_id_seq'::regclass);


--
-- TOC entry 4819 (class 2604 OID 16983)
-- Name: sys_role id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_role ALTER COLUMN id SET DEFAULT nextval('public.sys_role_id_seq'::regclass);


--
-- TOC entry 4831 (class 2604 OID 17815)
-- Name: sys_scheduled_task id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_scheduled_task ALTER COLUMN id SET DEFAULT nextval('public.sys_scheduled_task_id_seq'::regclass);


--
-- TOC entry 4832 (class 2604 OID 17826)
-- Name: sys_scheduled_task_log id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_scheduled_task_log ALTER COLUMN id SET DEFAULT nextval('public.sys_scheduled_task_log_id_seq'::regclass);


--
-- TOC entry 4820 (class 2604 OID 16996)
-- Name: sys_user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_user ALTER COLUMN id SET DEFAULT nextval('public.sys_user_id_seq'::regclass);


--
-- TOC entry 5062 (class 0 OID 16881)
-- Dependencies: 217
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
0002
\.


--
-- TOC entry 5064 (class 0 OID 16887)
-- Dependencies: 219
-- Data for Name: app_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.app_user (id, name, phone_code, phone, password, email, wx_openid, wx_unionid, deleted_at, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5099 (class 0 OID 17844)
-- Dependencies: 254
-- Data for Name: plugin_registry; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.plugin_registry (id, name, version, is_installed, installed_at, deleted_at, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5066 (class 0 OID 16922)
-- Dependencies: 221
-- Data for Name: sys_config; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_config (id, key, value, default_value, validation_rule, description, type, "group", is_system, deleted_at, created_at, updated_at) FROM stdin;
2	rate_limit.enabled	true	true	\N	限流总开关	BOOLEAN	SECURITY	t	\N	2026-05-24 17:05:48.363922+08	\N
3	rate_limit.ip_per_minute	120	120	\N	IP 全局限流（次/分钟）	NUMBER	SECURITY	t	\N	2026-05-24 17:05:48.363922+08	\N
4	rate_limit.user_per_minute	300	300	\N	用户限流（次/分钟）	NUMBER	SECURITY	t	\N	2026-05-24 17:05:48.363922+08	\N
5	rate_limit.login_fail_max	5	5	\N	登录失败上限次数	NUMBER	SECURITY	t	\N	2026-05-24 17:05:48.363922+08	\N
6	rate_limit.login_fail_window	600	600	\N	登录失败统计窗口（秒）	NUMBER	SECURITY	t	\N	2026-05-24 17:05:48.363922+08	\N
7	rate_limit.login_fail_block_ttl	1800	1800	\N	登录失败自动拉黑时长（秒）	NUMBER	SECURITY	t	\N	2026-05-24 17:05:48.363922+08	\N
8	rate_limit.blacklist_redis_ttl	86400	86400	\N	永久黑名单 Redis 兜底 TTL（秒）	NUMBER	SECURITY	t	\N	2026-05-24 17:05:48.363922+08	\N
9	rate_limit.whitelist_path_prefixes	["/docs","/redoc","/openapi.json","/admin/health"]	["/docs","/redoc","/openapi.json","/admin/health"]	\N	路径白名单前缀	JSON	SECURITY	t	\N	2026-05-24 17:05:48.363922+08	\N
10	rate_limit.whitelist_ips	[]	[]	\N	IP 白名单	JSON	SECURITY	t	\N	2026-05-24 17:05:48.363922+08	\N
11	rate_limit.path_rules	[]	[]	\N	路径细粒度限流规则	JSON	SECURITY	t	\N	2026-05-24 17:05:48.363922+08	\N
\.


--
-- TOC entry 5068 (class 0 OID 16933)
-- Dependencies: 223
-- Data for Name: sys_dict; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_dict (id, name, code, description, status, is_system, sort, deleted_at, created_at, updated_at) FROM stdin;
8	性别	gender	性别字典：男、女、未知	t	t	1	\N	2026-06-03 21:52:40.052698+08	2026-06-03 21:52:40.052698+08
\.


--
-- TOC entry 5076 (class 0 OID 17008)
-- Dependencies: 231
-- Data for Name: sys_dict_item; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_dict_item (id, dict_id, value, label, description, ext_info, status, sort, deleted_at, created_at, updated_at) FROM stdin;
7	8	1	男	\N	\N	t	1	\N	2026-06-03 21:52:40.052698+08	2026-06-03 21:52:40.052698+08
8	8	2	女	\N	\N	t	2	\N	2026-06-03 21:52:40.052698+08	2026-06-03 21:52:40.052698+08
9	8	0	未知	\N	\N	t	3	\N	2026-06-03 21:52:40.052698+08	2026-06-03 21:52:40.052698+08
\.


--
-- TOC entry 5082 (class 0 OID 17066)
-- Dependencies: 237
-- Data for Name: sys_export_task; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_export_task (id, task_name, module_key, template_id, query_params_json, created_by, status, total_rows, file_path, file_size, error_message, started_at, finished_at, deleted_at, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5084 (class 0 OID 17077)
-- Dependencies: 239
-- Data for Name: sys_export_template; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_export_template (id, name, module_key, columns, joins_config, description, created_by, deleted_at, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5090 (class 0 OID 17336)
-- Dependencies: 245
-- Data for Name: sys_file; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_file (id, original_name, stored_name, file_path, file_size, mime_type, extension, created_by, storage_platform, hash, deleted_at, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5088 (class 0 OID 17108)
-- Dependencies: 243
-- Data for Name: sys_ip_blacklist; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_ip_blacklist (id, ip, type, reason, expire_at, creator_id, deleted_at, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5086 (class 0 OID 17088)
-- Dependencies: 241
-- Data for Name: sys_login_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_login_log (id, username, ip, status, detail, user_agent, login_time, deleted_at, created_at, updated_at) FROM stdin;
2942832354664448	admin	127.0.0.1	t	登录成功	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	2026-06-04 17:20:58.130275+08	\N	2026-06-04 17:20:58.130275+08	\N
\.


--
-- TOC entry 5070 (class 0 OID 16954)
-- Dependencies: 225
-- Data for Name: sys_menu; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_menu (id, parent_id, name, path, component, redirect, permission, meta_icon, meta_hidden, meta_affix, meta_breadcrumb, status, type, sort, deleted_at, created_at, updated_at, is_system, meta_href, meta_keep_alive) FROM stdin;
2874692539129858	\N	log	/log	layout.base	\N	\N	mdi:file-document-outline	f	f	t	t	CATALOG	4	\N	2026-05-23 16:32:07.074678+08	2026-05-29 18:23:23.435562+08	t	\N	f
2942406613671936	\N	scheduler	/manage/scheduler	layout.base	/manage/scheduler/list	\N	material-symbols:schedule-outline	f	f	t	t	CATALOG	95	\N	2026-06-04 15:32:41.846173+08	\N	f	\N	f
2942406615113728	2942406613671936	manage_scheduler	/manage/scheduler/list	view.manage_scheduler	\N	sys:scheduler:list	material-symbols:task-alt-outline	f	f	t	t	MENU	1	\N	2026-06-04 15:32:41.875798+08	\N	f	\N	f
2942406615965696	2942406615113728	新增任务		\N	\N	sys:scheduler:add	\N	f	f	t	t	BUTTON	0	\N	2026-06-04 15:32:41.884895+08	\N	f	\N	f
2942406615965697	2942406615113728	编辑任务		\N	\N	sys:scheduler:edit	\N	f	f	t	t	BUTTON	0	\N	2026-06-04 15:32:41.884895+08	\N	f	\N	f
2942406615965698	2942406615113728	删除任务		\N	\N	sys:scheduler:delete	\N	f	f	t	t	BUTTON	0	\N	2026-06-04 15:32:41.884895+08	\N	f	\N	f
2942406615965699	2942406615113728	任务详情		\N	\N	sys:scheduler:detail	\N	f	f	t	t	BUTTON	0	\N	2026-06-04 15:32:41.88592+08	\N	f	\N	f
2942406615965700	2942406615113728	启停任务		\N	\N	sys:scheduler:status	\N	f	f	t	t	BUTTON	0	\N	2026-06-04 15:32:41.88592+08	\N	f	\N	f
2942406615965701	2942406615113728	手动执行		\N	\N	sys:scheduler:trigger	\N	f	f	t	t	BUTTON	0	\N	2026-06-04 15:32:41.88592+08	\N	f	\N	f
2942406615965702	2942406613671936	manage_scheduler-log	/manage/scheduler-log	view.manage_scheduler-log	\N	sys:scheduler:log:list	material-symbols:history	f	f	t	t	MENU	2	\N	2026-06-04 15:32:41.886454+08	\N	f	\N	f
2942406617800704	2942406615965702	日志详情		\N	\N	sys:scheduler:log:detail	\N	f	f	t	t	BUTTON	0	\N	2026-06-04 15:32:41.899353+08	\N	f	\N	f
2880160334618624	2874692539129861	manage_menu_list	\N	\N	\N	sys:menu:list	\N	t	f	f	t	BUTTON	1	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334618625	2874692539129861	manage_menu_add	\N	\N	\N	sys:menu:add	\N	t	f	f	t	BUTTON	2	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2942406617800705	2942406615965702	删除日志		\N	\N	sys:scheduler:log:delete	\N	f	f	t	t	BUTTON	0	\N	2026-06-04 15:32:41.899767+08	\N	f	\N	f
2880160334684160	2874692539129861	manage_menu_edit	\N	\N	\N	sys:menu:edit	\N	t	f	f	t	BUTTON	3	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334684161	2874692539129861	manage_menu_delete	\N	\N	\N	sys:menu:delete	\N	t	f	f	t	BUTTON	4	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334684162	2874692539129862	manage_role_list	\N	\N	\N	sys:role:list	\N	t	f	f	t	BUTTON	1	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334749696	2874692539129862	manage_role_add	\N	\N	\N	sys:role:add	\N	t	f	f	t	BUTTON	2	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334749697	2874692539129862	manage_role_edit	\N	\N	\N	sys:role:edit	\N	t	f	f	t	BUTTON	3	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334749698	2874692539129862	manage_role_delete	\N	\N	\N	sys:role:delete	\N	t	f	f	t	BUTTON	4	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334749699	2874692539129863	manage_user_list	\N	\N	\N	sys:user:list	\N	t	f	f	t	BUTTON	1	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334749700	2874692539129863	manage_user_add	\N	\N	\N	sys:user:add	\N	t	f	f	t	BUTTON	2	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334749701	2874692539129863	manage_user_edit	\N	\N	\N	sys:user:edit	\N	t	f	f	t	BUTTON	3	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2874692539129857	\N	manage	/manage	layout.base	\N	\N	mdi:cog	f	f	t	t	CATALOG	3	\N	2026-05-23 16:32:07.074678+08	2026-05-29 18:23:19.933746+08	t	\N	f
2880160334880773	2874692539129865	log_operation-log_list	\N	\N	\N	sys:oplog:list	\N	t	f	f	t	BUTTON	1	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334749702	2874692539129863	manage_user_delete	\N	\N	\N	sys:user:delete	\N	t	f	f	t	BUTTON	4	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334815232	2874692539129860	manage_dict_list	\N	\N	\N	sys:dict:list	\N	t	f	f	t	BUTTON	1	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334815233	2874692539129860	manage_dict_add	\N	\N	\N	sys:dict:add	\N	t	f	f	t	BUTTON	2	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334815234	2874692539129860	manage_dict_edit	\N	\N	\N	sys:dict:edit	\N	t	f	f	t	BUTTON	3	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334815235	2874692539129860	manage_dict_delete	\N	\N	\N	sys:dict:delete	\N	t	f	f	t	BUTTON	4	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334815236	2874692539129859	manage_config_list	\N	\N	\N	sys:config:list	\N	t	f	f	t	BUTTON	1	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334880768	2874692539129859	manage_config_add	\N	\N	\N	sys:config:add	\N	t	f	f	t	BUTTON	2	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334946304	2874692539129865	log_operation-log_delete	\N	\N	\N	sys:oplog:delete	\N	t	f	f	t	BUTTON	2	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334880769	2874692539129859	manage_config_edit	\N	\N	\N	sys:config:edit	\N	t	f	f	t	BUTTON	3	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334880770	2874692539129859	manage_config_delete	\N	\N	\N	sys:config:delete	\N	t	f	f	t	BUTTON	4	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334880771	2874692539129864	log_login-log_list	\N	\N	\N	sys:log:list	\N	t	f	f	t	BUTTON	1	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334880772	2874692539129864	log_login-log_delete	\N	\N	\N	sys:log:delete	\N	t	f	f	t	BUTTON	2	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2874692539129859	2874692539129857	manage_config	/manage/config	view.manage_config	\N	sys:config:list	\N	f	f	t	t	MENU	1	\N	2026-05-23 16:32:07.074678+08	\N	t	\N	f
2874692539129860	2874692539129857	manage_dict	/manage/dict	view.manage_dict	\N	sys:dict:list	\N	f	f	t	t	MENU	2	\N	2026-05-23 16:32:07.074678+08	\N	t	\N	f
2874692539129861	2874692539129857	manage_menu	/manage/menu	view.manage_menu	\N	sys:menu:list	\N	f	f	t	t	MENU	3	\N	2026-05-23 16:32:07.074678+08	\N	t	\N	f
2874692539129862	2874692539129857	manage_role	/manage/role	view.manage_role	\N	sys:role:list	\N	f	f	t	t	MENU	4	\N	2026-05-23 16:32:07.074678+08	\N	t	\N	f
2874692539129863	2874692539129857	manage_user	/manage/user	view.manage_user	\N	sys:user:list	\N	f	f	t	t	MENU	5	\N	2026-05-23 16:32:07.074678+08	\N	t	\N	f
2874692539129864	2874692539129858	log_login-log	/log/login-log	view.log_login-log	\N	sys:login-log:list	\N	f	f	t	t	MENU	1	\N	2026-05-23 16:32:07.074678+08	\N	t	\N	f
2880160334946305	2879249581154304	log_online-user_list	\N	\N	\N	sys:online:list	\N	t	f	f	t	BUTTON	1	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880160334946306	2879249581154304	log_online-user_kick	\N	\N	\N	sys:online:kick	\N	t	f	f	t	BUTTON	2	\N	2026-05-24 15:42:39.00864+08	\N	t	\N	f
2880487316987904	2880487316791296	manage_ip-blacklist_list	\N	\N	\N	sys:blacklist:list	\N	t	f	f	t	BUTTON	1	\N	2026-05-24 17:05:48.363922+08	\N	t	\N	f
2880487317118976	2880487316791296	manage_ip-blacklist_add	\N	\N	\N	sys:blacklist:add	\N	t	f	f	t	BUTTON	2	\N	2026-05-24 17:05:48.363922+08	\N	t	\N	f
2880487317118977	2880487316791296	manage_ip-blacklist_remove	\N	\N	\N	sys:blacklist:remove	\N	t	f	f	t	BUTTON	3	\N	2026-05-24 17:05:48.363922+08	\N	t	\N	f
2907499345027076	2874692539129857	manage_file	/manage/file	view.manage_file	\N	sys:file:list	\N	f	f	t	t	MENU	8	\N	2026-05-28 23:08:07.48867+08	\N	t	\N	f
2874692539129856	\N	home	/home	layout.base$view.home	\N	\N	mdi:monitor-dashboard	f	f	t	t	MENU	1	\N	2026-05-23 16:32:07.074678+08	2026-05-23 21:29:36.710187+08	t	\N	f
2874692539129865	2874692539129858	log_operation-log	/log/operation-log	view.log_operation-log	\N	sys:operation-log:list	\N	f	f	t	t	MENU	2	\N	2026-05-23 16:32:07.074678+08	2026-05-24 14:06:24.504114+08	t	\N	f
2880487316791296	2874692539129857	manage_ip-blacklist	/manage/ip-blacklist	view.manage_ip-blacklist	\N	sys:blacklist:list	\N	f	f	t	t	MENU	10	\N	2026-05-24 17:05:48.363922+08	\N	t	\N	f
2907499345027072	\N	demo	/demo	layout.base	\N	\N	arcticons:example	f	f	t	t	CATALOG	5	\N	2026-05-29 11:35:19.200988+08	2026-05-29 15:14:30.990737+08	t	\N	f
2886339278741504	2874692539129857	manage_announcement	/manage/announcement	view.manage_announcement	\N	sys:notice:list	\N	f	f	t	t	MENU	11	\N	2026-05-25 17:54:02.170377+08	\N	t	\N	f
2879249581154304	2874692539129857	log_online-user	/log/online-user	view.log_online-user	\N	sys:online-user:list	\N	f	f	t	t	MENU	9	\N	2026-05-24 11:51:01.998205+08	2026-05-24 14:06:39.545192+08	t	\N	f
2907499345027077	2907499345027076	manage_file_list	\N	\N	\N	sys:file:list	\N	f	f	t	t	BUTTON	1	\N	2026-05-28 23:08:07.48867+08	\N	t	\N	f
2886339279134720	2886339278741504	manage_announcement_list	\N	\N	\N	sys:notice:list	\N	t	f	f	t	BUTTON	1	\N	2026-05-25 17:54:02.170377+08	\N	t	\N	f
2886339279134721	2886339278741504	manage_announcement_add	\N	\N	\N	sys:notice:add	\N	t	f	f	t	BUTTON	2	\N	2026-05-25 17:54:02.170377+08	\N	t	\N	f
2886339279134722	2886339278741504	manage_announcement_edit	\N	\N	\N	sys:notice:edit	\N	t	f	f	t	BUTTON	3	\N	2026-05-25 17:54:02.170377+08	\N	t	\N	f
2886339279134723	2886339278741504	manage_announcement_delete	\N	\N	\N	sys:notice:delete	\N	t	f	f	t	BUTTON	4	\N	2026-05-25 17:54:02.170377+08	\N	t	\N	f
2886339279134724	2886339278741504	manage_announcement_publish	\N	\N	\N	sys:notice:publish	\N	t	f	f	t	BUTTON	5	\N	2026-05-25 17:54:02.170377+08	\N	t	\N	f
2907499345027078	2907499345027076	manage_file_upload	\N	\N	\N	sys:file:upload	\N	f	f	t	t	BUTTON	2	\N	2026-05-28 23:08:07.48867+08	\N	t	\N	f
2907499345027079	2907499345027076	manage_file_download	\N	\N	\N	sys:file:download	\N	f	f	t	t	BUTTON	3	\N	2026-05-28 23:08:07.48867+08	\N	t	\N	f
2907499345027074	2907499345027073	monitor_view	\N	\N	\N	sys:monitor:view	\N	t	f	f	t	BUTTON	1	\N	2026-05-28 20:18:46.884071+08	\N	t	\N	f
2907499345027080	2907499345027076	manage_file_delete	\N	\N	\N	sys:file:delete	\N	f	f	t	t	BUTTON	4	\N	2026-05-28 23:08:07.48867+08	\N	t	\N	f
2907499345027075	2907499345027072	demo_upload	/demo/upload	view.demo_upload	\N	\N	mdi:upload	f	f	t	t	MENU	5	\N	2026-05-28 23:08:07.48867+08	2026-05-29 15:13:41.448095+08	t	\N	f
2907499345027073	\N	monitor	/monitor	layout.base$view.monitor	\N	sys:monitor:list	mdi:chart-areaspline-variant	f	f	t	t	MENU	2	\N	2026-05-28 20:18:46.884071+08	2026-05-29 18:23:07.213857+08	t	\N	f
2907499345027081	2907499345027072	demo_dict	/demo/dict	view.demo_dict	\N	\N	mdi:book-alphabet	f	f	t	t	MENU	4	\N	2026-06-04 16:00:00+08	\N	t	\N	f
\.


--
-- TOC entry 5092 (class 0 OID 17404)
-- Dependencies: 247
-- Data for Name: sys_notice; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_notice (id, title, content, sender_id, sender_name, type, target_type, target_role_ids, target_user_ids, priority, status, published_at, deleted_at, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5094 (class 0 OID 17414)
-- Dependencies: 249
-- Data for Name: sys_notice_read; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_notice_read (id, user_id, notice_id, is_read, read_at, deleted_at, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5080 (class 0 OID 17055)
-- Dependencies: 235
-- Data for Name: sys_operation_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_operation_log (id, user_id, username, module, action, description, method, path, ip, request_params, response_code, elapsed_ms, deleted_at, created_at, updated_at, response_result) FROM stdin;
2942936298364928	2250298479026176	admin	sys	get	GET /admin/sys/notice/my/unread-count	GET	/admin/sys/notice/my/unread-count	127.0.0.1	\N	200	46.999999998661224	\N	2026-06-04 17:47:24.197104+08	\N	\N
2942959322537984	2250298479026176	admin	sys	get	GET /admin/sys/route/getPermissions	GET	/admin/sys/route/getPermissions	127.0.0.1	\N	200	62.000000001717126	\N	2026-06-04 17:53:15.517591+08	\N	\N
2942959335579648	2250298479026176	admin	sys	get	GET /admin/sys/notice/my/unread-count	GET	/admin/sys/notice/my/unread-count	127.0.0.1	\N	200	46.999999998661224	\N	2026-06-04 17:53:15.714938+08	\N	\N
2942959462457344	2250298479026176	admin	sys	get	GET /admin/sys/route/getPermissions	GET	/admin/sys/route/getPermissions	127.0.0.1	\N	200	94.00000000096043	\N	2026-06-04 17:53:17.650463+08	\N	\N
2942959477530624	2250298479026176	admin	sys	get	GET /admin/sys/notice/my/unread-count	GET	/admin/sys/notice/my/unread-count	127.0.0.1	\N	200	45.9999999984575	\N	2026-06-04 17:53:17.877624+08	\N	\N
2942935775518720	2250298479026176	admin	sys	get	GET /admin/sys/route/getPermissions	GET	/admin/sys/route/getPermissions	127.0.0.1	\N	200	125	\N	2026-06-04 17:47:16.213235+08	\N	\N
2942935793541120	2250298479026176	admin	sys	get	GET /admin/sys/notice/my/unread-count	GET	/admin/sys/notice/my/unread-count	127.0.0.1	\N	200	46.999999998661224	\N	2026-06-04 17:47:16.488943+08	\N	\N
2942936191410176	2250298479026176	admin	sys	get	GET /admin/sys/route/getPermissions	GET	/admin/sys/route/getPermissions	127.0.0.1	\N	200	94.00000000096043	\N	2026-06-04 17:47:22.56155+08	\N	\N
2942936200192000	2250298479026176	admin	sys	get	GET /admin/sys/route/isRouteExist	GET	/admin/sys/route/isRouteExist	127.0.0.1	{"query": {"routeName": "demo_dict"}}	200	94.00000000096043	\N	2026-06-04 17:47:22.696293+08	\N	\N
2943075753271296	2250298479026176	admin	sys	get	GET /admin/sys/route/getPermissions	GET	/admin/sys/route/getPermissions	127.0.0.1	\N	200	204.0000000015425	\N	2026-06-04 18:22:52.093217+08	\N	\N
2943075780337664	2250298479026176	admin	sys	get	GET /admin/sys/notice/my/unread-count	GET	/admin/sys/notice/my/unread-count	127.0.0.1	\N	200	78.00000000133878	\N	2026-06-04 18:22:52.518124+08	\N	\N
2943076030488576	2250298479026176	admin	sys	get	GET /admin/sys/dict/item/all/gender	GET	/admin/sys/dict/item/all/gender	127.0.0.1	\N	200	109.00000000037835	\N	2026-06-04 18:22:56.330688+08	\N	\N
2943101621116928	2250298479026176	admin	sys	get	GET /admin/sys/route/getPermissions	GET	/admin/sys/route/getPermissions	127.0.0.1	\N	200	62.999999998282874	\N	2026-06-04 18:29:26.821009+08	\N	\N
2943101664436224	2250298479026176	admin	sys	get	GET /admin/sys/dict/item/all/gender	GET	/admin/sys/dict/item/all/gender	127.0.0.1	\N	200	46.999999998661224	\N	2026-06-04 18:29:27.479399+08	\N	\N
2943100628836352	2250298479026176	admin	sys	get	GET /admin/sys/route/getPermissions	GET	/admin/sys/route/getPermissions	127.0.0.1	\N	200	157.00000000288128	\N	2026-06-04 18:29:11.544459+08	\N	\N
2943100704399360	2250298479026176	admin	sys	get	GET /admin/sys/route/getPermissions	GET	/admin/sys/route/getPermissions	127.0.0.1	\N	200	155.99999999903957	\N	2026-06-04 18:29:12.831003+08	\N	\N
2943101665615872	2250298479026176	admin	sys	get	GET /admin/sys/notice/my/unread-count	GET	/admin/sys/notice/my/unread-count	127.0.0.1	\N	200	61.99999999807915	\N	2026-06-04 18:29:27.501227+08	\N	\N
\.


--
-- TOC entry 5072 (class 0 OID 16980)
-- Dependencies: 227
-- Data for Name: sys_role; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_role (id, name, status, is_default, is_system, sort, deleted_at, created_at, updated_at, "desc") FROM stdin;
2902792101634048	测试	t	f	f	0	\N	2026-05-28 15:38:12.36984+08	\N	
2925633242210304	111	t	f	f	0	\N	2026-06-01 16:27:00.51223+08	2026-06-01 18:20:48.097208+08	
\.


--
-- TOC entry 5077 (class 0 OID 17022)
-- Dependencies: 232
-- Data for Name: sys_role_menu; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_role_menu (role_id, menu_id, permission) FROM stdin;
2902792101634048	2874692539129856	read
2902792101634048	2907499345027073	read
2902792101634048	2907499345027074	read
2902792101634048	2880160334684162	read
2902792101634048	2880160334749697	read
2902792101634048	2880160334946306	read
2902792101634048	2886339279134721	read
2902792101634048	2880160334684160	read
2902792101634048	2880160334749700	read
2902792101634048	2880487317118977	read
2902792101634048	2886339279134723	read
2902792101634048	2880160334618624	read
2902792101634048	2874692539129861	read
2902792101634048	2880487316791296	read
2902792101634048	2907499345027079	read
2902792101634048	2880160334749696	read
2902792101634048	2874692539129863	read
2902792101634048	2907499345027077	read
2902792101634048	2880160334749698	read
2902792101634048	2880487316987904	read
2902792101634048	2886339279134724	read
2902792101634048	2880160334749701	read
2902792101634048	2886339278741504	read
2902792101634048	2880160334684161	read
2902792101634048	2886339279134722	read
2902792101634048	2880160334946305	read
2902792101634048	2907499345027080	read
2902792101634048	2880160334749699	read
2902792101634048	2886339279134720	read
2902792101634048	2880160334618625	read
2902792101634048	2880487317118976	read
2902792101634048	2907499345027076	read
2902792101634048	2907499345027078	read
2902792101634048	2880160334749702	read
2902792101634048	2874692539129862	read
2902792101634048	2879249581154304	read
2925633242210304	2874692539129858	read
2925633242210304	2907499345027073	read
2925633242210304	2874692539129864	read
2925633242210304	2874692539129863	read
2925633242210304	2880160334880772	read
2925633242210304	2880160334880773	read
2925633242210304	2880160334749699	read
2925633242210304	2880160334684162	read
2925633242210304	2874692539129862	read
2925633242210304	2874692539129856	read
2925633242210304	2880160334749700	read
2925633242210304	2880160334749702	read
2925633242210304	2880160334749696	read
2925633242210304	2874692539129865	read
2925633242210304	2880160334946304	read
2925633242210304	2880160334749697	read
2925633242210304	2907499345027074	read
2925633242210304	2880160334749701	read
2925633242210304	2880160334880771	read
2925633242210304	2880160334749698	read
2902792101634048	2907499345027081	read
\.


--
-- TOC entry 5096 (class 0 OID 17812)
-- Dependencies: 251
-- Data for Name: sys_scheduled_task; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_scheduled_task (id, name, task_key, cron_expression, description, trigger_type, trigger_params, status, module, function_path, is_system, last_run_at, next_run_at, last_status, timeout, max_retries, concurrent_policy, deleted_at, created_at, updated_at) FROM stdin;
2942449943060480	刷新限流配置缓存	system.refresh_rate_limit_config	25	定时从数据库刷新限流参数到内存缓存，避免请求路径上回源	interval	{"seconds": 25}	t	modules.scheduler.tasks.rate_limit_config	modules.scheduler.tasks.rate_limit_config.refresh_rate_limit_config	t	2026-06-04 18:31:01.180338+08	2026-06-04 18:31:26.151522+08	success	300	0	skip	\N	2026-06-04 15:43:43.002522+08	2026-06-04 18:31:01.221759+08
2938394705010689	清理过期登录日志	system.cleanup_login_logs	0 4 * * *	自动清理30天前的登录日志	cron		t	modules.scheduler.tasks.builtin	modules.scheduler.tasks.builtin.cleanup_login_logs	t	2026-06-03 23:11:05.638119+08	2026-06-05 04:00:00+08	success	300	0	skip	\N	2026-06-03 22:32:24.97958+08	2026-06-04 15:36:45.388728+08
2938394705010688	清理过期操作日志	system.cleanup_operation_logs	0 3 * * *	自动清理30天前的操作日志	cron	\N	t	modules.scheduler.tasks.builtin	modules.scheduler.tasks.builtin.cleanup_operation_logs	t	2026-06-04 15:36:50.704196+08	2026-06-05 03:00:00+08	success	300	0	skip	\N	2026-06-03 22:32:24.969304+08	2026-06-04 15:36:50.741534+08
\.


--
-- TOC entry 5098 (class 0 OID 17823)
-- Dependencies: 253
-- Data for Name: sys_scheduled_task_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_scheduled_task_log (id, task_id, task_name, task_key, status, start_time, end_time, duration_ms, result, error_message, retry_count, triggered_by, deleted_at, created_at, updated_at) FROM stdin;
\.


--
-- TOC entry 5074 (class 0 OID 16993)
-- Dependencies: 229
-- Data for Name: sys_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_user (id, username, password, nickname, email, phone, avatar, last_login_at, last_login_ip, status, is_superuser, deleted_at, created_at, updated_at, last_tenant_id) FROM stdin;
2250298479026176	admin	$2b$12$MPXWjrezSywnujoarubtJuKUJKBXugHEEqobTbIWtbJRXAp2aaTUy	超级管理员	admin@example.com	13800138000		2026-06-04 17:20:58.10803+08	127.0.0.1	t	t	\N	2026-02-02 10:00:29.81271+08	2026-06-04 17:20:58.111531+08	2919523120979968
2337926656696320	qqqq	$2b$12$xeY6/LrdH7XFnkrnKop95Opc99IX1ckUBFbf6op5jcZhg5yHU4U6O	qq			\N	2026-05-30 22:30:19.86873+08	127.0.0.1	t	f	\N	2026-02-17 21:25:29.695889+08	2026-05-30 22:30:19.869799+08	\N
\.


--
-- TOC entry 5078 (class 0 OID 17037)
-- Dependencies: 233
-- Data for Name: sys_user_role; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sys_user_role (user_id, role_id) FROM stdin;
2337926656696320	2925633242210304
\.


--
-- TOC entry 5376 (class 0 OID 0)
-- Dependencies: 218
-- Name: app_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.app_user_id_seq', 1, false);


--
-- TOC entry 5377 (class 0 OID 0)
-- Dependencies: 220
-- Name: sys_config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sys_config_id_seq', 11, true);


--
-- TOC entry 5378 (class 0 OID 0)
-- Dependencies: 222
-- Name: sys_dict_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sys_dict_id_seq', 8, true);


--
-- TOC entry 5379 (class 0 OID 0)
-- Dependencies: 230
-- Name: sys_dict_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sys_dict_item_id_seq', 9, true);


--
-- TOC entry 5380 (class 0 OID 0)
-- Dependencies: 236
-- Name: sys_export_task_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sys_export_task_id_seq', 1, false);


--
-- TOC entry 5381 (class 0 OID 0)
-- Dependencies: 238
-- Name: sys_export_template_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sys_export_template_id_seq', 1, false);


--
-- TOC entry 5382 (class 0 OID 0)
-- Dependencies: 244
-- Name: sys_file_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sys_file_id_seq', 1, false);


--
-- TOC entry 5383 (class 0 OID 0)
-- Dependencies: 242
-- Name: sys_ip_blacklist_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sys_ip_blacklist_id_seq', 1, false);


--
-- TOC entry 5384 (class 0 OID 0)
-- Dependencies: 240
-- Name: sys_login_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sys_login_log_id_seq', 1, false);


--
-- TOC entry 5385 (class 0 OID 0)
-- Dependencies: 224
-- Name: sys_menu_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sys_menu_id_seq', 1, false);


--
-- TOC entry 5386 (class 0 OID 0)
-- Dependencies: 246
-- Name: sys_notice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sys_notice_id_seq', 1, false);


--
-- TOC entry 5387 (class 0 OID 0)
-- Dependencies: 248
-- Name: sys_notice_read_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sys_notice_read_id_seq', 1, false);


--
-- TOC entry 5388 (class 0 OID 0)
-- Dependencies: 234
-- Name: sys_operation_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sys_operation_log_id_seq', 1, false);


--
-- TOC entry 5389 (class 0 OID 0)
-- Dependencies: 226
-- Name: sys_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sys_role_id_seq', 1, false);


--
-- TOC entry 5390 (class 0 OID 0)
-- Dependencies: 250
-- Name: sys_scheduled_task_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sys_scheduled_task_id_seq', 1, false);


--
-- TOC entry 5391 (class 0 OID 0)
-- Dependencies: 252
-- Name: sys_scheduled_task_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sys_scheduled_task_log_id_seq', 1, false);


--
-- TOC entry 5392 (class 0 OID 0)
-- Dependencies: 228
-- Name: sys_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sys_user_id_seq', 1, false);


--
-- TOC entry 4835 (class 2606 OID 16885)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 4837 (class 2606 OID 16894)
-- Name: app_user app_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.app_user
    ADD CONSTRAINT app_user_pkey PRIMARY KEY (id);


--
-- TOC entry 4910 (class 2606 OID 17849)
-- Name: plugin_registry plugin_registry_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.plugin_registry
    ADD CONSTRAINT plugin_registry_pkey PRIMARY KEY (id);


--
-- TOC entry 4842 (class 2606 OID 16929)
-- Name: sys_config sys_config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_config
    ADD CONSTRAINT sys_config_pkey PRIMARY KEY (id);


--
-- TOC entry 4861 (class 2606 OID 17015)
-- Name: sys_dict_item sys_dict_item_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_dict_item
    ADD CONSTRAINT sys_dict_item_pkey PRIMARY KEY (id);


--
-- TOC entry 4846 (class 2606 OID 16940)
-- Name: sys_dict sys_dict_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_dict
    ADD CONSTRAINT sys_dict_pkey PRIMARY KEY (id);


--
-- TOC entry 4873 (class 2606 OID 17073)
-- Name: sys_export_task sys_export_task_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_export_task
    ADD CONSTRAINT sys_export_task_pkey PRIMARY KEY (id);


--
-- TOC entry 4877 (class 2606 OID 17084)
-- Name: sys_export_template sys_export_template_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_export_template
    ADD CONSTRAINT sys_export_template_pkey PRIMARY KEY (id);


--
-- TOC entry 4888 (class 2606 OID 17343)
-- Name: sys_file sys_file_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_file
    ADD CONSTRAINT sys_file_pkey PRIMARY KEY (id);


--
-- TOC entry 4885 (class 2606 OID 17114)
-- Name: sys_ip_blacklist sys_ip_blacklist_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_ip_blacklist
    ADD CONSTRAINT sys_ip_blacklist_pkey PRIMARY KEY (id);


--
-- TOC entry 4881 (class 2606 OID 17095)
-- Name: sys_login_log sys_login_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_login_log
    ADD CONSTRAINT sys_login_log_pkey PRIMARY KEY (id);


--
-- TOC entry 4849 (class 2606 OID 16961)
-- Name: sys_menu sys_menu_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_menu
    ADD CONSTRAINT sys_menu_pkey PRIMARY KEY (id);


--
-- TOC entry 4891 (class 2606 OID 17411)
-- Name: sys_notice sys_notice_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_notice
    ADD CONSTRAINT sys_notice_pkey PRIMARY KEY (id);


--
-- TOC entry 4896 (class 2606 OID 17419)
-- Name: sys_notice_read sys_notice_read_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_notice_read
    ADD CONSTRAINT sys_notice_read_pkey PRIMARY KEY (id);


--
-- TOC entry 4869 (class 2606 OID 17062)
-- Name: sys_operation_log sys_operation_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_operation_log
    ADD CONSTRAINT sys_operation_log_pkey PRIMARY KEY (id);


--
-- TOC entry 4863 (class 2606 OID 17026)
-- Name: sys_role_menu sys_role_menu_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_role_menu
    ADD CONSTRAINT sys_role_menu_pkey PRIMARY KEY (role_id, menu_id);


--
-- TOC entry 4852 (class 2606 OID 16989)
-- Name: sys_role sys_role_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_role
    ADD CONSTRAINT sys_role_name_key UNIQUE (name);


--
-- TOC entry 4854 (class 2606 OID 16987)
-- Name: sys_role sys_role_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_role
    ADD CONSTRAINT sys_role_pkey PRIMARY KEY (id);


--
-- TOC entry 4906 (class 2606 OID 17830)
-- Name: sys_scheduled_task_log sys_scheduled_task_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_scheduled_task_log
    ADD CONSTRAINT sys_scheduled_task_log_pkey PRIMARY KEY (id);


--
-- TOC entry 4902 (class 2606 OID 17819)
-- Name: sys_scheduled_task sys_scheduled_task_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_scheduled_task
    ADD CONSTRAINT sys_scheduled_task_pkey PRIMARY KEY (id);


--
-- TOC entry 4858 (class 2606 OID 17000)
-- Name: sys_user sys_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_user
    ADD CONSTRAINT sys_user_pkey PRIMARY KEY (id);


--
-- TOC entry 4865 (class 2606 OID 17041)
-- Name: sys_user_role sys_user_role_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_user_role
    ADD CONSTRAINT sys_user_role_pkey PRIMARY KEY (user_id, role_id);


--
-- TOC entry 4898 (class 2606 OID 17421)
-- Name: sys_notice_read uix_user_notice; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_notice_read
    ADD CONSTRAINT uix_user_notice UNIQUE (user_id, notice_id);


--
-- TOC entry 4838 (class 1259 OID 16895)
-- Name: ix_app_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_app_user_id ON public.app_user USING btree (id);


--
-- TOC entry 4907 (class 1259 OID 17852)
-- Name: ix_plugin_registry_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_plugin_registry_id ON public.plugin_registry USING btree (id);


--
-- TOC entry 4908 (class 1259 OID 17853)
-- Name: ix_plugin_registry_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_plugin_registry_name ON public.plugin_registry USING btree (name);


--
-- TOC entry 4839 (class 1259 OID 16930)
-- Name: ix_sys_config_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_config_id ON public.sys_config USING btree (id);


--
-- TOC entry 4840 (class 1259 OID 16931)
-- Name: ix_sys_config_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_config_key ON public.sys_config USING btree (key);


--
-- TOC entry 4843 (class 1259 OID 16941)
-- Name: ix_sys_dict_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_dict_code ON public.sys_dict USING btree (code);


--
-- TOC entry 4844 (class 1259 OID 16942)
-- Name: ix_sys_dict_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_dict_id ON public.sys_dict USING btree (id);


--
-- TOC entry 4859 (class 1259 OID 17021)
-- Name: ix_sys_dict_item_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_dict_item_id ON public.sys_dict_item USING btree (id);


--
-- TOC entry 4870 (class 1259 OID 17074)
-- Name: ix_sys_export_task_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_export_task_id ON public.sys_export_task USING btree (id);


--
-- TOC entry 4871 (class 1259 OID 17075)
-- Name: ix_sys_export_task_module_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sys_export_task_module_key ON public.sys_export_task USING btree (module_key);


--
-- TOC entry 4874 (class 1259 OID 17085)
-- Name: ix_sys_export_template_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_export_template_id ON public.sys_export_template USING btree (id);


--
-- TOC entry 4875 (class 1259 OID 17086)
-- Name: ix_sys_export_template_module_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sys_export_template_module_key ON public.sys_export_template USING btree (module_key);


--
-- TOC entry 4886 (class 1259 OID 17344)
-- Name: ix_sys_file_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_file_id ON public.sys_file USING btree (id);


--
-- TOC entry 4882 (class 1259 OID 17117)
-- Name: ix_sys_ip_blacklist_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_ip_blacklist_id ON public.sys_ip_blacklist USING btree (id);


--
-- TOC entry 4883 (class 1259 OID 17118)
-- Name: ix_sys_ip_blacklist_ip; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_ip_blacklist_ip ON public.sys_ip_blacklist USING btree (ip);


--
-- TOC entry 4878 (class 1259 OID 17096)
-- Name: ix_sys_login_log_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_login_log_id ON public.sys_login_log USING btree (id);


--
-- TOC entry 4879 (class 1259 OID 17097)
-- Name: ix_sys_login_log_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sys_login_log_username ON public.sys_login_log USING btree (username);


--
-- TOC entry 4847 (class 1259 OID 16967)
-- Name: ix_sys_menu_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_menu_id ON public.sys_menu USING btree (id);


--
-- TOC entry 4889 (class 1259 OID 17412)
-- Name: ix_sys_notice_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_notice_id ON public.sys_notice USING btree (id);


--
-- TOC entry 4892 (class 1259 OID 17422)
-- Name: ix_sys_notice_read_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_notice_read_id ON public.sys_notice_read USING btree (id);


--
-- TOC entry 4893 (class 1259 OID 17423)
-- Name: ix_sys_notice_read_notice_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sys_notice_read_notice_id ON public.sys_notice_read USING btree (notice_id);


--
-- TOC entry 4894 (class 1259 OID 17424)
-- Name: ix_sys_notice_read_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sys_notice_read_user_id ON public.sys_notice_read USING btree (user_id);


--
-- TOC entry 4866 (class 1259 OID 17063)
-- Name: ix_sys_operation_log_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_operation_log_id ON public.sys_operation_log USING btree (id);


--
-- TOC entry 4867 (class 1259 OID 17098)
-- Name: ix_sys_operation_log_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sys_operation_log_user_id ON public.sys_operation_log USING btree (user_id);


--
-- TOC entry 4850 (class 1259 OID 16991)
-- Name: ix_sys_role_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_role_id ON public.sys_role USING btree (id);


--
-- TOC entry 4899 (class 1259 OID 17820)
-- Name: ix_sys_scheduled_task_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_scheduled_task_id ON public.sys_scheduled_task USING btree (id);


--
-- TOC entry 4903 (class 1259 OID 17831)
-- Name: ix_sys_scheduled_task_log_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_scheduled_task_log_id ON public.sys_scheduled_task_log USING btree (id);


--
-- TOC entry 4904 (class 1259 OID 17832)
-- Name: ix_sys_scheduled_task_log_task_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sys_scheduled_task_log_task_id ON public.sys_scheduled_task_log USING btree (task_id);


--
-- TOC entry 4900 (class 1259 OID 17821)
-- Name: ix_sys_scheduled_task_task_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_scheduled_task_task_key ON public.sys_scheduled_task USING btree (task_key);


--
-- TOC entry 4855 (class 1259 OID 17005)
-- Name: ix_sys_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_user_id ON public.sys_user USING btree (id);


--
-- TOC entry 4856 (class 1259 OID 17006)
-- Name: ix_sys_user_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sys_user_username ON public.sys_user USING btree (username);


--
-- TOC entry 4912 (class 2606 OID 17016)
-- Name: sys_dict_item sys_dict_item_dict_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_dict_item
    ADD CONSTRAINT sys_dict_item_dict_id_fkey FOREIGN KEY (dict_id) REFERENCES public.sys_dict(id) ON DELETE CASCADE;


--
-- TOC entry 4911 (class 2606 OID 17356)
-- Name: sys_menu sys_menu_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_menu
    ADD CONSTRAINT sys_menu_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.sys_menu(id) ON DELETE CASCADE;


--
-- TOC entry 4913 (class 2606 OID 17346)
-- Name: sys_role_menu sys_role_menu_menu_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_role_menu
    ADD CONSTRAINT sys_role_menu_menu_id_fkey FOREIGN KEY (menu_id) REFERENCES public.sys_menu(id) ON DELETE CASCADE;


--
-- TOC entry 4914 (class 2606 OID 17351)
-- Name: sys_role_menu sys_role_menu_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_role_menu
    ADD CONSTRAINT sys_role_menu_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.sys_role(id) ON DELETE CASCADE;


--
-- TOC entry 4915 (class 2606 OID 17042)
-- Name: sys_user_role sys_user_role_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_user_role
    ADD CONSTRAINT sys_user_role_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.sys_role(id) ON DELETE CASCADE;


--
-- TOC entry 4916 (class 2606 OID 17047)
-- Name: sys_user_role sys_user_role_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sys_user_role
    ADD CONSTRAINT sys_user_role_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.sys_user(id) ON DELETE CASCADE;


-- Completed on 2026-06-08 14:59:38

--
-- PostgreSQL database dump complete
--

\unrestrict 5PxxLp13VmOwQ6yD6RfOx6kZCLhavTSebbm2LlHnfy2NjzZ9fthUgMk8NVj4w19

