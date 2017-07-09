import re
import subprocess

from _utils import *


class DockerCategory:
    def __init__(self, base_image_name, order, title, path, options=None):
        self.base_image_name = base_image_name
        self.order = order
        self.title = title
        self.path = path
        self.options = []

        re_compile_option = re.compile(r'^([0-9]+)\.(.*)\.docker')

        option_listdir = os.listdir(self.path)
        # 각 카테고리(00.template, 01.base...)내의 파일들을 순회
        for option in option_listdir:
            # 03.extra의 01.debug, 01.production...도 순회
            cur_option_order = re_compile_option.search(option).group(1)
            # Option인스턴스의 order가 cur_option_order(00, 01등)과 같은 Option이 self.options리스트 목록에 없을 경우 새로 만들어 줌
            if not any(option.order == cur_option_order for option in self.options):
                cur_option = DockerCategoryOption(category=self, order=cur_option_order)
                self.options.append(cur_option)
            # 같은 옵션번호를 가질 경우 cur_option은 같은 DockerCategoryOption객체를 사용
            cur_option = next(
                (option for option in self.options if option.order == cur_option_order), None)
            # 파일 하나하나가 서브옵션이므로 각 루프마다 서브옵션을 생성, 추가
            cur_sub_option = DockerCategorySubOption(
                parent_option=cur_option,
                order=cur_option_order,
                title=re_compile_option.search(option).group(2)
            )
            cur_option.sub_options.append(cur_sub_option)

    def __str__(self):
        ret = 'DockerCategory({}.{})\n'.format(self.order, self.title)
        items = {
            'order': self.order,
            'title': self.title,
            'path': self.path,
            'options': self.options
        }
        for k, v in items.items():
            ret += '  {:10}: {}\n'.format(k, v)
        ret = ret[:-1]
        return ret

    @property
    def is_require_select_option(self):
        for option in self.options:
            if option.is_require_select_option:
                return True
        return False

    @property
    def unique_options(self):
        if self.is_require_select_option:
            raise Exception('require option select')
        return [sub_option for option in self.options for sub_option in option.sub_options]

    def select_options(self):
        for option in self.options:
            option.select_sub_option()


class DockerCategoryOption:
    def __init__(self, category, order, options=None):
        self.category = category
        self.order = order
        self.sub_options = options if options else []
        self.selected_sub_option = None

    def __repr__(self):
        return 'Option(Category:[{}], Order:[{}])'.format(
            self.category.title,
            self.order,
        )

    @property
    def is_require_select_option(self):
        if len(self.sub_options) > 1:
            return True
        return False

    @property
    def unique_sub_option(self):
        if self.is_require_select_option:
            raise Exception('require select sub option')
        else:
            return self.sub_options[0]

    def select_sub_option(self):
        self.selected_sub_option = None
        if self.is_require_select_option:
            select_string = 'Category({}.{})\n - Option({})\n -- SubOption select:\n'.format(
                self.category.order,
                self.category.title,
                self.order
            )
            for index, sub_option in enumerate(self.sub_options):
                select_string += '  {}.{}\n'.format(
                    index + 1,
                    sub_option.title
                )
            select_string = select_string[:-1]
            while True:
                print(select_string)
                selected_sub_option_index = input('  > Select SubOption: ')
                try:
                    selected_sub_option = self.sub_options[int(selected_sub_option_index) - 1]
                    self.selected_sub_option = selected_sub_option
                    print('')
                    break
                except ValueError as e:
                    print('  ! Input value error ({})\n'.format(e))
                except IndexError as e:
                    print('  ! Selected SubOption index is not valid ({})\n'.format(e))

        else:
            self.selected_sub_option = self.unique_sub_option
            # print('Don\'t need select SubOption. This Option has unique SubOption')
        return self.selected_sub_option


class DockerCategorySubOption:
    def __init__(self, parent_option, order, title):
        self.parent_option = parent_option
        self.order = order
        self.title = title

    def __repr__(self):
        return self.info

    @property
    def info(self):
        return '{}-{}-{}-{}'.format(
            self.parent_option.category.base_image_name,
            self.parent_option.category.title,
            self.parent_option.order,
            self.title
        )

    @property
    def path(self):
        return '{}/{}.{}.docker'.format(
            self.parent_option.category.path,
            self.order,
            self.title
        )


class DockerBuild:
    def __init__(self):
        self.categories = []
        self.root_image_name = config_public['docker']['DockerfileBaseName']
        self.start_image = None
        self.end_image = None
        self.is_production = False
        conf_dir = CONF_DOCKER_DIR
        re_compile_category = re.compile(r'^([0-9]+)\.(.*)')
        docker_conf_listdir = os.listdir(conf_dir)

        for category in docker_conf_listdir:
            if os.path.isdir(os.path.join(conf_dir, category)):
                cur_category = DockerCategory(
                    base_image_name=self.root_image_name,
                    order=re_compile_category.search(category).group(1),
                    title=re_compile_category.search(category).group(2),
                    path=os.path.join(CONF_DOCKER_DIR, category),
                )
                self.categories.append(cur_category)

        self.print_intro()
        self.set_options()
        self.set_start_image()
        self.set_end_image()
        self.make_dockerfiles()

    @staticmethod
    def print_intro():
        intro_string = '=== DockerBuild ==='
        print(intro_string)

    def set_options(self):
        for category in self.categories:
            category.select_options()

    @property
    def selected_options(self):
        """
        각 카테고리(template, base, common, extra)의 
        옵션 (00, 01, 02...등)에
        선택한 서브옵션 (03.extra - 01 - debug or production)들로 이루어진 리스트를 리턴
        서브옵션이 선택되지 않았을 경우 None이 원소로 반환됨
        :return: list(DockerCategorySubOption)
        """
        return [option.selected_sub_option for category in self.categories for option in
                category.options]

    @property
    def is_selected_all_sub_options(self):
        """
        모든 카테고리의 옵션에 대해 서브옵션을 선택했는지 여부 반환
        :return: Bool, 모든 서브옵션을 선택했는지
        """
        return all(self.selected_options)

    def set_start_image(self):
        select_string = 'Select start image:\n'
        select_string += '  {}.{}\n'.format(
            0, config_public['docker']['rootImageName'],
        )
        for index, option in enumerate(self.selected_options):
            select_string += '  {}.{}\n'.format(
                index + 1,
                option.info
            )
        select_string = select_string[:-1]
        while True:
            print(select_string)
            selected_option_index = input(
                '  > Select image number (default: {}.{}): '.format(
                    0, config_public['docker']['rootImageName']
                )
            )
            try:
                if selected_option_index == '' or selected_option_index == '0':
                    self.start_image = None
                else:
                    self.start_image = self.selected_options[int(selected_option_index) - 1]
                print('')
                break
            except ValueError as e:
                print('  ! Input value error ({})\n'.format(e))
            except IndexError as e:
                print('  ! Selected SubOption index is not valid ({})\n'.format(e))

    def set_end_image(self):
        start_index = self.selected_options.index(self.start_image) if self.start_image else 0
        select_string = 'Select end image:\n'
        for index, option in enumerate(self.selected_options):
            if index < start_index:
                continue
            select_string += '  {}.{}\n'.format(
                index + 1,
                option.info
            )
        select_string = select_string[:-1]
        while True:
            print(select_string)
            default_index = len(self.selected_options) - 1
            selected_option_index = input(
                '  > Select image number (default: {}.{}): '.format(
                    default_index + 1,
                    self.selected_options[default_index].info
                )
            )
            try:
                if selected_option_index == '':
                    selected_option_index = default_index + 1
                int_selected_option_index = int(selected_option_index) - 1
                self.end_image = self.selected_options[int_selected_option_index]
                print('')
                # 만약 선택된 index가 default_index(마지막 인덱스)와 같을 경우 (끝 이미지를 선택한 경우)
                # is_production을 True로 설정하고,
                # 이후 make_dockerfiles에서 프로젝트폴더에 Dockerfile을 생성해준다.
                if int_selected_option_index == default_index:
                    self.is_production = True
                break
            except ValueError as e:
                print('  ! Input value error ({})\n'.format(e))
            except IndexError as e:
                print('  ! Selected SubOption index is not valid ({})\n'.format(e))

    def make_dockerfiles(self):
        start_index = self.selected_options.index(self.start_image) if self.start_image else None
        end_index = self.selected_options.index(self.end_image)
        root_image_name = config_public['docker']['rootImageName']

        template = open(os.path.join(CONF_DOCKER_DIR, 'template.docker')).read()
        print('== Make Dockerfiles ==')
        # ROOT_DIR부터 .dockerfiles디렉토리 생성 (임시 Dockerfile들 저장소)
        os.makedirs(os.path.join(ROOT_DIR, '.dockerfiles'), exist_ok=True)
        dockerfiles_dir = os.path.join(ROOT_DIR, '.dockerfiles')
        for index, option in enumerate(self.selected_options):
            if (start_index and index < start_index) or index > end_index:
                continue
            file_name = 'Dockerfile.{}.{}.{}.{}'.format(
                option.parent_option.category.order,
                option.parent_option.category.title,
                option.parent_option.order,
                option.title)
            print(file_name)
            prev_image = self.selected_options[index - 1].info if index > 0 else root_image_name
            cur_template = template.format(
                from_image=prev_image,
                maintainer=config_secret_common['docker']['maintainer'],
                content=open(os.path.join(option.path), 'rt').read(),
            )
            open(os.path.join(dockerfiles_dir, file_name), 'wt').write(cur_template)
            # is_production일 경우 마지막 loop의 파일을 프로젝트폴더/Dockerfile에 기록
            if self.is_production and index == len(self.selected_options) - 1:
                cur_template = template.format(
                    from_image=config_public['docker']['dockerHubImageName'],
                    maintainer=config_secret_common['docker']['maintainer'],
                    content=open(os.path.join(option.path), 'rt').read(),
                )
                open(os.path.join(ROOT_DIR, 'Dockerfile'), 'wt').write(cur_template)

            build_command_template = 'docker build . -t {name} -f {dockerfile_name}'
            build_command = build_command_template.format(
                name=option.info,
                dockerfile_name=os.path.join(dockerfiles_dir, file_name),
            )
            subprocess.run(build_command, shell=True)

